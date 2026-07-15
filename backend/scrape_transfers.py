import requests
import time
import re
from database import SessionLocal
from models import Player, Team, PlayerTeamHistory

def parse_team_id(href):
    """Extracts team ID from a href like '/barcelona/transfers/verein/131/saison_id/2005'"""
    if not href:
        return None
    match = re.search(r'\/verein\/(\d+)', href)
    if match:
        return int(match.group(1))
    return None

def rebuild_transfer_history(db, player):
    tm_api_id = player.api_id
    if not tm_api_id:
        return False
        
    url = f"https://www.transfermarkt.com.tr/ceapi/transferHistory/list/{tm_api_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            print(f"[{player.id}] API Hatası: {res.status_code}")
            return False
            
        data = res.json()
        transfers = data.get("transfers", [])
        
        # Transfers usually come newest first. Let's reverse them to chronological (oldest to newest).
        transfers.reverse()
        
        # Get all valid teams mapped by api_id
        valid_teams = {t.api_id: t.id for t in db.query(Team).all()}
        
        new_histories = []
        current_history = None
        
        for t in transfers:
            to_club = t.get("to", {})
            date_str = t.get("dateUnformatted") # "2023-07-15"
            
            # Extract year
            start_year = None
            if date_str and len(date_str) >= 4:
                try:
                    start_year = int(date_str[:4])
                except ValueError:
                    pass
                    
            team_api_id = parse_team_id(to_club.get("href"))
            
            # If the current history exists, the new transfer means he left the current team.
            # Set the end_year of the previous team to this transfer's start_year.
            if current_history and start_year:
                current_history.end_year = start_year
                
            if team_api_id and team_api_id in valid_teams:
                # Add the new team to history
                current_history = PlayerTeamHistory(
                    player_id=player.id,
                    team_id=valid_teams[team_api_id],
                    start_year=start_year,
                    end_year=None, # Will be set by next transfer, or stays None if it's the last one
                    is_active=False
                )
                new_histories.append(current_history)
            else:
                # He transferred to a team we don't track.
                # So we just end his previous history, but we don't start a new tracked one.
                current_history = None
                
        # If there are histories, mark the very last one as potentially active
        if new_histories and player.is_active:
            new_histories[-1].is_active = True
            
        if new_histories:
            # Delete old history
            db.query(PlayerTeamHistory).filter(PlayerTeamHistory.player_id == player.id).delete()
            # Bulk insert new history
            db.add_all(new_histories)
            db.commit()
            safe_name = player.known_as.encode('ascii', 'ignore').decode('utf-8')
            print(f"[BAŞARILI] {safe_name}: {len(new_histories)} takım geçmişi işlendi.")
            return True
        else:
            safe_name = player.known_as.encode('ascii', 'ignore').decode('utf-8')
            print(f"[ATLANDI] {safe_name}: Kayda değer transfer bulunamadı.")
            return True
            
    except Exception as e:
        safe_name = player.known_as.encode('ascii', 'ignore').decode('utf-8') if player.known_as else "Bilinmeyen"
        print(f"[{player.id}] {safe_name} Hata: {str(e)}")
        db.rollback()
        return False

def main():
    db = SessionLocal()
    # Sadece en popüler (milli maç sayısı yüksek) ilk 500 oyuncuyu işleyelim ki hemen test edebilelim.
    players = db.query(Player).order_by(Player.international_caps.desc()).limit(500).all()
    print(f"Öncelikli test için en popüler {len(players)} oyuncunun transfer geçmişi güncellenecek...")
    
    success_count = 0
    
    for idx, player in enumerate(players):
        print(f"İşleniyor ({idx+1}/{len(players)})... ", end="")
        if rebuild_transfer_history(db, player):
            success_count += 1
        time.sleep(1.0) # Rate limiting
        
    print(f"İşlem tamamlandı! Başarılı: {success_count}/{len(players)}")

if __name__ == "__main__":
    main()
