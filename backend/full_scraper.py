import requests
import time
import json
import os
import datetime
from database import SessionLocal
from models import Player, PlayerStats, Team, PlayerTeamHistory
import unicodedata
from sqlalchemy.exc import SQLAlchemyError

def log_progress(player_id, status_file="scraper_progress.txt"):
    with open(status_file, "w") as f:
        f.write(str(player_id))

def get_last_processed(status_file="scraper_progress.txt"):
    if os.path.exists(status_file):
        with open(status_file, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                return int(content)
    return 0

def fetch_and_update_stats(db, player):
    tm_api_id = player.api_id
    if not tm_api_id:
        return False
        
    url_game = f"https://tmapi.transfermarkt.technology/player/{tm_api_id}/performance-game"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        res = requests.get(url_game, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"[{player.id}] {player.search_name} için API hatası: {res.status_code}")
            return False
            
        json_data = res.json()
        matches = json_data.get("data", {}).get("performance", [])
        
        # Olan istatistikleri silelim
        db.query(PlayerStats).filter(PlayerStats.player_id == player.id).delete()
        
        comp_stats = {}
        nat_caps, nat_goals, nat_assists, nat_yellow, nat_red = 0, 0, 0, 0, 0
        
        def _safe_count(val):
            if val is None:
                return 0
            if isinstance(val, (int, float)):
                return int(val)
            if isinstance(val, list):
                return len(val)
            return 1 if val else 0
            
        def _get_val(d, keys):
            for k in keys:
                if d.get(k) is not None:
                    return d.get(k)
            return 0

        for match in matches:
            game_info = match.get("gameInformation", {})
            stats = match.get("statistics", {})
            event_stats = stats.get("goalStatistics", {}) or {}
            card_stats = stats.get("cardStatistics", {}) or {}
            play_stats = stats.get("playingTimeStatistics", {}) or {}
            
            comp_id = game_info.get("competitionId", "UNKNOWN")
            season_id = str(game_info.get("seasonId", "Unknown"))
            is_national = game_info.get("isNationalGame", False)
            participation = stats.get("generalStatistics", {}).get("participationState", "")
            
            # Sadece oyuncunun sahaya çıktığı (oynadığı) maçları say
            if participation != "played":
                continue
            
            # Hazırlık maçlarını (FS = Freundschaftsspiele) saymıyoruz
            if comp_id == "FS":
                continue
            
            goals = _safe_count(_get_val(event_stats, ["goalsScoredTotalOfficial", "goalsScoredTotal"]))
            assists = _safe_count(_get_val(event_stats, ["assistsOfficial", "assists"]))
            yellow = _safe_count(_get_val(card_stats, ["yellowCardNet", "yellowCardGross", "yellowCards"]))
            red = _safe_count(_get_val(card_stats, ["redCard", "redCards", "redCardNet", "yellowRedCard"]))
            minutes = _safe_count(play_stats.get("playedMinutes", 0))
            
            if is_national:
                nat_caps += 1
                nat_goals += goals
                nat_assists += assists
                nat_yellow += yellow
                nat_red += red
                
            key = (comp_id, season_id)
            if key not in comp_stats:
                comp_stats[key] = {"games": 0, "goals": 0, "assists": 0, "yellow": 0, "red": 0, "minutes": 0}
                
            comp_stats[key]["games"] += 1
            comp_stats[key]["goals"] += goals
            comp_stats[key]["assists"] += assists
            comp_stats[key]["yellow"] += yellow
            comp_stats[key]["red"] += red
            comp_stats[key]["minutes"] += minutes
            
        player.international_caps = nat_caps
        player.international_goals = nat_goals
        player.international_assists = nat_assists
        player.international_yellow_cards = nat_yellow
        player.international_red_cards = nat_red
        
        # Son güncellenme tarihini ve aktiflik durumunu belirle
        player.last_updated = datetime.datetime.now()
        max_season = max([int(season_id) for _, season_id in comp_stats.keys() if season_id.isdigit()], default=0)
        player.is_active = True if max_season >= 2024 else False
        
        for (comp_id, season_id), st in comp_stats.items():
            new_stat = PlayerStats(
                player_id=player.id,
                league_name=comp_id.upper(),
                season=season_id,
                appearances=st["games"],
                goals=st["goals"],
                assists=st["assists"],
                yellow_cards=st["yellow"],
                red_cards=st["red"],
                minutes_played=st["minutes"]
            )
            db.add(new_stat)
            
        db.commit()
        
        # 2. Kulüp Geçmişi
        club_performances = []
        url_clubs = f"https://www.transfermarkt.com.tr/ceapi/player/{tm_api_id}/performanceperclub"
        try:
            res_clubs = requests.get(url_clubs, headers=headers, timeout=10)
            if res_clubs.status_code == 200:
                data_clubs = res_clubs.json()
                club_performances = data_clubs.get("performances", [])
                for perf in club_performances:
                    entity = perf.get("entity", {})
                    club_id_str = entity.get("id")
                    club_name = entity.get("name")
                    
                    if not club_id_str or not club_name:
                        continue
                        
                    club_id = int(club_id_str)
                    
                    team = db.query(Team).filter(Team.api_id == club_id).first()
                    if not team:
                        search_n = unicodedata.normalize('NFKD', club_name).encode('ASCII', 'ignore').decode('utf-8').lower()
                        team = db.query(Team).filter(Team.search_name == search_n).first()
                        if not team:
                            team = db.query(Team).filter(Team.name == club_name).first()
                            
                        if team:
                            team.api_id = club_id
                        else:
                            team = Team(
                                api_id=club_id,
                                name=club_name,
                                search_name=search_n,
                                logo_url=entity.get("logo")
                            )
                            db.add(team)
                            db.flush()
                    
                    history = db.query(PlayerTeamHistory).filter(
                        PlayerTeamHistory.player_id == player.id,
                        PlayerTeamHistory.team_id == team.id
                    ).first()
                    
                    if not history:
                        new_history = PlayerTeamHistory(
                            player_id=player.id,
                            team_id=team.id
                        )
                        db.add(new_history)
                        
                db.commit()
        except Exception as e:
            print(f"[{player.id}] {player.search_name} kulüp geçmişi hatası: {str(e)}")
            db.rollback()

        print(f"[BAŞARILI] {player.known_as or player.search_name.title()} | {len(club_performances)} Kulüp | {len(comp_stats)} Turnuva/Sezon | {nat_caps} Milli Maç ({nat_goals} Gol)")
        return True
    except Exception as e:
        print(f"[{player.id}] {player.search_name} güncellenirken hata: {str(e)}")
        db.rollback()
        return False

def main():
    db = SessionLocal()
    last_id = get_last_processed()
    print(f"Bot başlıyor... Kaldığı yer (Player ID): {last_id}")
    
    players = db.query(Player).filter(Player.id > last_id).order_by(Player.id.asc()).all()
    print(f"Toplam güncellenecek oyuncu sayısı: {len(players)}")
    
    for player in players:
        success = fetch_and_update_stats(db, player)
        if success:
            log_progress(player.id)
            time.sleep(1.5) # Rate limit koruması
        else:
            time.sleep(3.0)
            
if __name__ == "__main__":
    main()
