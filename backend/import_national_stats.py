import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Player

DATABASE_URL = "sqlite:///football_trivia.db"

def run_import():
    print("Veritabanına bağlanılıyor...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("players.csv okunuyor...")
    df = pd.read_csv("data/players.csv", usecols=['player_id', 'international_caps', 'international_goals'])
    
    print("Oyuncu verileri güncelleniyor...")
    players = session.query(Player).all()
    player_dict = {p.api_id: p for p in players if p.api_id}
    
    updated = 0
    for _, row in df.iterrows():
        p_api = row['player_id']
        if p_api in player_dict:
            player = player_dict[p_api]
            # NaN (boş) değerleri 0 yap
            caps = row['international_caps']
            goals = row['international_goals']
            
            player.international_caps = int(caps) if pd.notna(caps) else 0
            player.international_goals = int(goals) if pd.notna(goals) else 0
            updated += 1
            
    session.commit()
    print(f"Toplam {updated} oyuncunun milli takım verisi başarıyla güncellendi!")

if __name__ == "__main__":
    run_import()
