import os
import sys

# Windows'ta çalışırken SQLite (V1) ve Postgres (V2) bağlantıları gerekecek
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # V1 (Yerel SQLite)
    engine_v1 = create_engine("sqlite:///./football_trivia.db", connect_args={"check_same_thread": False})
    SessionLocalV1 = sessionmaker(autocommit=False, autoflush=False, bind=engine_v1)
    
    # V2 (Postgres Digital Ocean)
    # Konsolda $env:DATABASE_URL_V2="..." şeklinde tanımlı olmalı
    db_url_v2 = os.getenv("DATABASE_URL_V2")
    if not db_url_v2:
        print("HATA: Lütfen önce konsolda DATABASE_URL_V2 değişkenini tanımlayın!")
        sys.exit(1)
        
    engine_v2 = create_engine(db_url_v2)
    SessionLocalV2 = sessionmaker(autocommit=False, autoflush=False, bind=engine_v2)
    
    # Modeller
    from models import Player as PlayerV1, Team as TeamV1
    from models_v2 import Player as PlayerV2, Team as TeamV2, Base
    
except ImportError as e:
    print(f"Modül Hatası: {e}")
    sys.exit(1)

def migrate():
    # Önce tabloların V2'de olduğundan emin olalım
    Base.metadata.create_all(bind=engine_v2)
    
    db_v1 = SessionLocalV1()
    db_v2 = SessionLocalV2()
    
    print("====== V1'DEN V2 POSTGRESQL'E DEV GÖÇ BAŞLIYOR ======")
    
    # 1. Takımları Göç Ettir
    print("1. Takımlar kopyalanıyor...")
    teams_v1 = db_v1.query(TeamV1).all()
    v2_teams = []
    for t in teams_v1:
        v2_teams.append(TeamV2(
            id=t.id,
            api_id=t.api_id,
            name=t.name,
            logo_url=t.logo_url
        ))
    
    # Önce eski takımları temizle (varsa)
    db_v2.query(TeamV2).delete()
    db_v2.add_all(v2_teams)
    db_v2.commit()
    print(f"{len(v2_teams)} takım başarıyla Postgres'e aktarıldı!")
    
    # 2. Oyuncuları Göç Ettir
    print("2. Oyuncular kopyalanıyor (Bu birkaç saniye sürebilir)...")
    players_v1 = db_v1.query(PlayerV1).all()
    v2_players = []
    for p in players_v1:
        v2_players.append(PlayerV2(
            id=p.id, # ID'leri aynı tutalım
            api_id=p.api_id,
            name=f"{p.first_name or ''} {p.last_name or ''}".strip() or p.known_as,
            known_as=p.known_as,
            search_name=p.search_name,
            nationality=p.nationality,
            birth_date=p.birth_date,
            position=p.position,
            image_url=p.image_url,
            is_active=p.is_active,
            last_updated=p.last_updated
        ))
        
    db_v2.query(PlayerV2).delete()
    # Çoklu ekleme (Chunking) ile daha hızlı ve güvenli aktarım
    chunk_size = 5000
    for i in range(0, len(v2_players), chunk_size):
        chunk = v2_players[i:i+chunk_size]
        db_v2.add_all(chunk)
        db_v2.commit()
        print(f"  - {min(i+chunk_size, len(v2_players))}/{len(v2_players)} oyuncu aktarıldı...")
        
    print(f"{len(v2_players)} oyuncu başarıyla Postgres'e aktarıldı!")
    
    db_v1.close()
    db_v2.close()
    print("GÖÇ TAMAMLANDI! Artık dağıtık scraper'ı çalıştırabilirsiniz.")

if __name__ == "__main__":
    migrate()
