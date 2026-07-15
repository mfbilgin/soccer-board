import datetime
from sqlalchemy import text, func
from database import SessionLocal
from models import Player, PlayerStats

def migrate():
    db = SessionLocal()
    
    print("Tablolara yeni kolonlar ekleniyor...")
    try:
        db.execute(text("ALTER TABLE players ADD COLUMN last_updated DATETIME;"))
        db.commit()
        print("last_updated kolonu eklendi.")
    except Exception as e:
        print("last_updated kolonu zaten var olabilir veya bir hata oluştu:", e)
        db.rollback()

    try:
        db.execute(text("ALTER TABLE players ADD COLUMN is_active BOOLEAN DEFAULT 1;"))
        db.commit()
        print("is_active kolonu eklendi.")
    except Exception as e:
        print("is_active kolonu zaten var olabilir veya bir hata oluştu:", e)
        db.rollback()
        
    print("Mevcut oyuncuların aktiflik durumları güncelleniyor...")
    players = db.query(Player).all()
    updated_count = 0
    now = datetime.datetime.now()
    
    for p in players:
        # Oyuncunun oynadığı son sezonu bul
        max_season = db.query(func.max(PlayerStats.season)).filter(PlayerStats.player_id == p.id).scalar()
        
        # 2024 ve sonrası sezonlarda oynamışsa aktif sayılır (2024/2025 veya 2025/2026 vb.)
        if max_season and str(max_season) >= "2024":
            p.is_active = True
        else:
            p.is_active = False
            
        p.last_updated = now
        updated_count += 1
        
    db.commit()
    print(f"Toplam {updated_count} oyuncu başarıyla güncellendi ve migration tamamlandı!")
    db.close()

if __name__ == "__main__":
    migrate()
