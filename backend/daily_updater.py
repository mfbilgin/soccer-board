import time
import datetime
from database import SessionLocal
from models import Player
from full_scraper import fetch_and_update_stats

def update_active_players():
    db = SessionLocal()
    
    # 24 saatten eski güncellenmiş (veya hiç güncellenmemiş) aktif oyuncuları bul
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    
    players_to_update = db.query(Player).filter(
        Player.is_active == True,
        (Player.last_updated == None) | (Player.last_updated < yesterday)
    ).order_by(Player.id.asc()).all()
    
    print(f"Toplam güncellenecek aktif oyuncu sayısı: {len(players_to_update)}")
    
    for player in players_to_update:
        print(f"Güncelleniyor: {player.known_as or player.full_name} (ID: {player.id})")
        try:
            success = fetch_and_update_stats(db, player)
            if success:
                time.sleep(1.5) # API limitlerine takılmamak için bekle
            else:
                time.sleep(3.0)
        except Exception as e:
            print(f"HATA ({player.known_as}): {e}")
            time.sleep(5.0)
            
    print("Günlük güncelleme tamamlandı!")
    db.close()

if __name__ == "__main__":
    update_active_players()
