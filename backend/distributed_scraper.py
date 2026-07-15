import argparse
import logging
import sys
import requests
import time
import re
from database_v2 import SessionLocalV2
from models_v2 import Player, Team, Competition, PlayerClubStat, PlayerTransfer, PlayerHonour, PlayerNationalStat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
CEAPI_BASE = "https://www.transfermarkt.com.tr/ceapi"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# --- CACHES FOR PERFORMANCE ---
TEAM_CACHE = {}
COMP_CACHE = {}

def get_or_create_team(db, api_id, name, is_national=False):
    if not api_id:
        return None
        
    if api_id in TEAM_CACHE:
        return TEAM_CACHE[api_id]
        
    team = db.query(Team).filter_by(api_id=api_id).first()
    if not team:
        t_type = 'national' if is_national else 'club'
        team = Team(api_id=api_id, name=name or f"Team {api_id}", type=t_type)
        db.add(team)
        db.flush() # ID'yi almak için flush
    
    TEAM_CACHE[api_id] = team.id
    return team.id

def get_or_create_competition(db, api_id, name):
    if not api_id:
        return None
        
    if api_id in COMP_CACHE:
        return COMP_CACHE[api_id]
        
    comp = db.query(Competition).filter_by(api_id=str(api_id)).first()
    if not comp:
        comp = Competition(api_id=str(api_id), name=name or str(api_id))
        db.add(comp)
        db.flush()
        
    COMP_CACHE[api_id] = comp.id
    return comp.id

def fetch_json(url):
    try:
        time.sleep(0.5) # Rate limit protection
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        pass
    return None

def parse_team_id(href):
    if not href:
        return None
    match = re.search(r'\/verein\/(\d+)', href)
    if match:
        return int(match.group(1))
    return None

def process_player(db, player):
    api_id = player.api_id
    if not api_id:
        return False
        
    player_db_id = player.id
    
    # 1. Performance (Club & National Stats) via TMAPI
    perf = fetch_json(f"{TMAPI_BASE}/player/{api_id}/performance-game")
    if perf and 'data' in perf and 'performance' in perf['data']:
        club_stats_agg = {}
        nat_stats_agg = {}
        
        for match in perf['data']['performance']:
            game_info = match.get('gameInformation', {})
            stats = match.get('statistics', {})
            gen_stats = stats.get('generalStatistics', {})
            event_stats = stats.get('goalStatistics', {}) or {}
            card_stats = stats.get('cardStatistics', {}) or {}
            play_stats = stats.get('playingTimeStatistics', {}) or {}
            
            if gen_stats.get('participationState') != 'played':
                continue
            
            comp_id_api = game_info.get('competitionId')
            if comp_id_api == 'FS':
                continue
                
            season_id = game_info.get('seasonId', '0')
            club_id = match.get('clubsInformation', {}).get('club', {}).get('clubId')
            # Takım ismini performance verisi üzerinden getirmek için fallback:
            club_name = f"Team {club_id}" if club_id else "Unknown"
            
            comp_name = comp_id_api
            
            # Helper for getting values safely
            def _get_val(d, keys):
                for k in keys:
                    if d.get(k) is not None:
                        return d.get(k)
                return 0
                
            def _to_int(val):
                if val is None: return 0
                if isinstance(val, dict): return 0
                try: return int(val)
                except: return 0

            goals = _to_int(_get_val(event_stats, ["goalsScoredTotalOfficial", "goalsScoredTotal"]))
            assists = _to_int(_get_val(event_stats, ["assistsOfficial", "assists"]))
            yc = _to_int(_get_val(card_stats, ["yellowCardNet", "yellowCardGross", "yellowCards"]))
            rc = _to_int(_get_val(card_stats, ["redCard", "redCards", "redCardNet", "yellowRedCard"]))
            mins = _to_int(play_stats.get("playedMinutes", 0))
            is_starting = 1 if play_stats.get("isStarting") else 0
            pen_goals = _to_int(event_stats.get("penaltyShooterGoalsScored", 0))
            pen_misses = _to_int(event_stats.get("penaltyShooterMisses", 0))
            shirt = gen_stats.get("shirtNumber")
            
            is_national = game_info.get('isNationalGame', False)
            db_team_id = get_or_create_team(db, club_id, club_name, is_national=is_national)
            if not db_team_id:
                continue
                
            if is_national:
                key = db_team_id
                if key not in nat_stats_agg:
                    nat_stats_agg[key] = {'caps': 0, 'goals': 0, 'assists': 0}
                nat_stats_agg[key]['caps'] += 1
                nat_stats_agg[key]['goals'] += goals
                nat_stats_agg[key]['assists'] += assists
            else:
                db_comp_id = get_or_create_competition(db, comp_id_api, comp_name)
                key = (db_team_id, db_comp_id, season_id)
                if key not in club_stats_agg:
                    club_stats_agg[key] = {'app': 0, 'g': 0, 'a': 0, 'y': 0, 'r': 0, 'm': 0, 'st': 0, 'pg': 0, 'pm': 0, 'shirt': None}
                
                club_stats_agg[key]['app'] += 1
                club_stats_agg[key]['g'] += goals
                club_stats_agg[key]['a'] += assists
                club_stats_agg[key]['y'] += yc
                club_stats_agg[key]['r'] += rc
                club_stats_agg[key]['m'] += mins
                club_stats_agg[key]['st'] += is_starting
                club_stats_agg[key]['pg'] += pen_goals
                club_stats_agg[key]['pm'] += pen_misses
                if shirt:
                    club_stats_agg[key]['shirt'] = shirt # Son maçın forması yazılır

        # Veritabanına Yaz
        for (t_id, c_id, s_id), st in club_stats_agg.items():
            db_stat = db.query(PlayerClubStat).filter_by(player_id=player_db_id, team_id=t_id, competition_id=c_id, season=str(s_id)).first()
            if not db_stat:
                db_stat = PlayerClubStat(player_id=player_db_id, team_id=t_id, competition_id=c_id, season=str(s_id))
                db.add(db_stat)
            db_stat.appearances = st['app']
            db_stat.goals = st['g']
            db_stat.assists = st['a']
            db_stat.yellow_cards = st['y']
            db_stat.red_cards = st['r']
            db_stat.minutes_played = st['m']
            db_stat.started_matches = st['st']
            db_stat.penalty_goals = st['pg']
            db_stat.penalty_misses = st['pm']
            db_stat.shirt_number = st['shirt']
            
        for t_id, st in nat_stats_agg.items():
            n_stat = db.query(PlayerNationalStat).filter_by(player_id=player_db_id, team_id=t_id).first()
            if not n_stat:
                n_stat = PlayerNationalStat(player_id=player_db_id, team_id=t_id)
                db.add(n_stat)
            n_stat.caps = st['caps']
            n_stat.goals = st['goals']
            n_stat.assists = st['assists']
            
        db.commit()

    # 2. Transfers via CEAPI
    transfers_data = fetch_json(f"{CEAPI_BASE}/transferHistory/list/{api_id}")
    if transfers_data and 'transfers' in transfers_data:
        for t in transfers_data['transfers']:
            from_club = t.get('from', {})
            to_club = t.get('to', {})
            
            f_api = parse_team_id(from_club.get('href'))
            t_api = parse_team_id(to_club.get('href'))
            
            f_id = get_or_create_team(db, f_api, from_club.get('clubName')) if f_api else None
            t_id = get_or_create_team(db, t_api, to_club.get('clubName')) if t_api else None
            
            if not t_id:
                continue
                
            # Emeklilik kontrolü
            if t_api == 123:
                player.is_active = False
                
            date_str = t.get('dateUnformatted')
            if not date_str:
                continue
                
            db_trans = db.query(PlayerTransfer).filter_by(player_id=player_db_id, from_team_id=f_id, to_team_id=t_id, transfer_date=date_str).first()
            if not db_trans:
                fee = str(t.get('fee', 'Unknown'))
                mval = str(t.get('marketValue', '-'))
                db.add(PlayerTransfer(player_id=player_db_id, from_team_id=f_id, to_team_id=t_id, transfer_date=date_str, transfer_fee=fee, market_value=mval))
        db.commit()

    return True

def run_distributed_scraping(start_id: int, end_id: int, active_only: bool = False):
    logging.info(f"Scraping başlıyor... Veritabanı Oyuncu ID Aralığı: {start_id} - {end_id}")
    
    db = SessionLocalV2()
    query = db.query(Player).filter(Player.id >= start_id, Player.id <= end_id)
    
    if active_only:
        logging.info("Sadece Aktif (is_active=True) oyuncular taranacak!")
        query = query.filter(Player.is_active == True)
        
    players = query.order_by(Player.id.asc()).all()
    
    if not players:
        logging.warning("Bu aralıkta hiçbir oyuncu bulunamadı! Önce migrate işlemini yaptınız mı?")
        db.close()
        return
        
    logging.info(f"İşlenecek Toplam Oyuncu: {len(players)}")
    
    success_count = 0
    for idx, player in enumerate(players):
        try:
            if idx % 50 == 0:
                logging.info(f"İlerleme: {idx}/{len(players)} - Şu An: {player.name}")
            if process_player(db, player):
                success_count += 1
        except Exception as e:
            logging.error(f"Hata {player.name} (ID: {player.id}): {str(e)}")
            db.rollback()
            continue
            
    db.close()
    logging.info(f"Bitti! {success_count} oyuncu başarıyla güncellendi.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Distributed V2 Scraper")
    parser.add_argument("--start", type=int, required=True, help="Başlangıç DB ID (Örn: 1)")
    parser.add_argument("--end", type=int, required=True, help="Bitiş DB ID (Örn: 16000)")
    parser.add_argument("--active-only", action="store_true", help="Sadece aktif (emekli olmayan) oyuncuları tara")
    
    args = parser.parse_args()
    run_distributed_scraping(args.start, args.end, args.active_only)

