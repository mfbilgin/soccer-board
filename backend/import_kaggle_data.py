import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Player, Team, PlayerTeamHistory, PlayerStats
import os

DATABASE_URL = "sqlite:///football_trivia.db"
DATA_DIR = "data"

def run_etl():
    print("ETL Scripti Başlatılıyor...")
    if not os.path.exists(DATA_DIR):
        print(f"Hata: '{DATA_DIR}' klasörü bulunamadı. Lütfen Kaggle CSV dosyalarını bu klasöre koyun.")
        return

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    clubs_path = os.path.join(DATA_DIR, "clubs.csv")
    players_path = os.path.join(DATA_DIR, "players.csv")
    transfers_path = os.path.join(DATA_DIR, "transfers.csv")

    # 1. Takımları Aktar (Clubs)
    if os.path.exists(clubs_path):
        print("1. Clubs (Takımlar) yükleniyor...")
        df_clubs = pd.read_csv(clubs_path)
        added_clubs = 0
        for _, row in df_clubs.iterrows():
            if not session.query(Team).filter_by(api_id=row['club_id']).first():
                team = Team(
                    api_id=row['club_id'],
                    name=row['name'],
                    country="Unknown" # Kaggle datasetinde lig id var ama ülke adı statik gelmeyebilir
                )
                session.add(team)
                added_clubs += 1
        session.commit()
        print(f"-> {added_clubs} yeni takım başarıyla eklendi.")

    # 2. Futbolcuları Aktar (Players)
    if os.path.exists(players_path):
        print("2. Players (Futbolcular) yükleniyor...")
        df_players = pd.read_csv(players_path)
        added_players = 0
        for _, row in df_players.iterrows():
            if not session.query(Player).filter_by(api_id=row['player_id']).first():
                player = Player(
                    api_id=row['player_id'],
                    known_as=row['name'],
                    nationality=row['country_of_citizenship'] if pd.notna(row['country_of_citizenship']) else None,
                    birth_date=row['date_of_birth'] if pd.notna(row['date_of_birth']) else None,
                    height_cm=row['height_in_cm'] if pd.notna(row['height_in_cm']) else None,
                    position=row['position'] if pd.notna(row['position']) else None,
                    image_url=row['image_url'] if 'image_url' in row and pd.notna(row['image_url']) else None
                )
                session.add(player)
                added_players += 1
        session.commit()
        print(f"-> {added_players} yeni oyuncu başarıyla eklendi.")

    # 3. Kariyer Geçmişini Aktar (Transfers)
    if os.path.exists(transfers_path):
        print("3. Transfers (Kariyer Geçmişi) yükleniyor...")
        df_transfers = pd.read_csv(transfers_path)
        
        # Optimize lookup: Veritabanındaki tüm oyuncuları ram'e al
        player_map = {p.api_id: p.id for p in session.query(Player).all()}
        team_map = {t.api_id: t.id for t in session.query(Team).all()}
        
        history_objects = []
        for _, row in df_transfers.iterrows():
            p_api_id = row['player_id']
            to_team_api_id = row['to_club_id']
            
            # Sistemde (veritabanında) olan bir oyuncu ve takımsa kaydet
            if p_api_id in player_map and to_team_api_id in team_map:
                start_year = None
                if pd.notna(row['transfer_date']):
                    start_year = int(str(row['transfer_date']).split('-')[0])
                
                h = PlayerTeamHistory(
                    player_id=player_map[p_api_id],
                    team_id=team_map[to_team_api_id],
                    start_year=start_year,
                    end_year=None, # Şimdilik null kalabilir
                    is_active=False
                )
                history_objects.append(h)
        
        if history_objects:
            session.bulk_save_objects(history_objects)
            session.commit()
            print(f"-> {len(history_objects)} kariyer (transfer) kaydı başarıyla eklendi.")

    # 4. İstatistikleri Aktar (PlayerStats)
    appearances_path = os.path.join(DATA_DIR, "appearances.csv")
    if os.path.exists(appearances_path):
        print("4. Appearances (Oyuncu İstatistikleri) yükleniyor... (Bu işlem birkaç saniye sürebilir)")
        # Sadece ihtiyacımız olan sütunları belleğe alalım
        df_app = pd.read_csv(appearances_path, usecols=['player_id', 'competition_id', 'goals', 'assists', 'yellow_cards', 'red_cards'])
        
        # Oyuncu ve Turnuvaya göre gruplayıp istatistikleri toplayalım
        print("-> İstatistikler hesaplanıyor (Pandas GroupBy)...")
        df_grouped = df_app.groupby(['player_id', 'competition_id']).agg({
            'goals': 'sum',
            'assists': 'sum',
            'yellow_cards': 'sum',
            'red_cards': 'sum',
            'player_id': 'count' # appearance sayısı olarak kullanacağız
        }).rename(columns={'player_id': 'appearances'}).reset_index()

        player_map = {p.api_id: p.id for p in session.query(Player).all()}
        
        stats_objects = []
        for _, row in df_grouped.iterrows():
            p_api_id = row['player_id']
            if p_api_id in player_map:
                stat = PlayerStats(
                    player_id=player_map[p_api_id],
                    league_name=row['competition_id'],
                    goals=int(row['goals']),
                    assists=int(row['assists']),
                    yellow_cards=int(row['yellow_cards']),
                    red_cards=int(row['red_cards']),
                    appearances=int(row['appearances'])
                )
                stats_objects.append(stat)
        
        if stats_objects:
            # Önce eski istatistikleri temizleyelim ki çift kayıt olmasın (UPSERT mantığı)
            session.query(PlayerStats).delete()
            session.bulk_save_objects(stats_objects)
            session.commit()
            print(f"-> {len(stats_objects)} turnuva istatistik kaydı başarıyla eklendi.")

if __name__ == "__main__":
    run_etl()
    print("ETL İşlemi Tamamlandı!")
