import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Player, Team, PlayerTeamHistory

DATABASE_URL = "sqlite:///football_trivia.db"

def run_fix():
    print("Veritabanına bağlanılıyor...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("appearances.csv okunuyor (Bu biraz sürebilir)...")
    df = pd.read_csv("data/appearances.csv", usecols=['player_id', 'player_club_id'])
    
    print("Oyuncu-Takım eşleşmeleri sayılıyor (Hatalı/Tek maçlık kayıtları ayıklamak için)...")
    # Grupla ve her takımda kaç maça çıktığını say
    pair_counts = df.groupby(['player_id', 'player_club_id']).size().reset_index(name='match_count')
    
    # Kaggle veri setinde veri kazıma (scraping) hataları var. Bazen oyuncuyu 1 maçlığına rakip takıma yazmış.
    # Gerçekten o takımda oynamış sayılması için en az 3 maça çıkmış olmasını şart koşuyoruz.
    valid_pairs = pair_counts[pair_counts['match_count'] >= 3]

    print("Veritabanı haritaları oluşturuluyor...")
    player_map = {p.api_id: p.id for p in session.query(Player).all()}
    team_map = {t.api_id: t.id for t in session.query(Team).all()}

    print("Mevcut kariyer geçmişleri temizleniyor...")
    session.query(PlayerTeamHistory).delete()
    session.commit()

    print("Yeni filtrelenmiş kariyer geçmişleri hazırlanıyor...")
    history_objects = []
    
    for _, row in valid_pairs.iterrows():
        p_api = row['player_id']
        t_api = row['player_club_id']
        
        if p_api in player_map and t_api in team_map:
            h = PlayerTeamHistory(
                player_id=player_map[p_api],
                team_id=team_map[t_api]
            )
            history_objects.append(h)

    print(f"Toplam {len(history_objects)} adet DOĞRULANMIŞ kariyer geçmişi bulundu. Veritabanına yazılıyor...")
    
    # Bulk insert işlemi
    chunk_size = 10000
    for i in range(0, len(history_objects), chunk_size):
        chunk = history_objects[i:i + chunk_size]
        session.bulk_save_objects(chunk)
        session.commit()

    print("İşlem tamamlandı!")

if __name__ == "__main__":
    run_fix()
