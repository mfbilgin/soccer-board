from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Player, Team, PlayerTeamHistory

DATABASE_URL = "sqlite:///football_trivia.db"

def seed_initial_data():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Seeding test data into the database...")
    
    # 1. Takımları Ekle
    rm_team = session.query(Team).filter_by(name="Real Madrid").first()
    if not rm_team:
        rm_team = Team(name="Real Madrid", country="Spain")
        fenerbahce = Team(name="Fenerbahce", country="Turkey")
        bayern = Team(name="Bayern Munich", country="Germany")
        session.add_all([rm_team, fenerbahce, bayern])
        session.commit()
        print("Takımlar eklendi (Real Madrid, Fenerbahce, Bayern Munich).")

    # Yeniden sorgula id'leri alabilmek için
    rm_team = session.query(Team).filter_by(name="Real Madrid").first()
    fenerbahce = session.query(Team).filter_by(name="Fenerbahce").first()
    bayern = session.query(Team).filter_by(name="Bayern Munich").first()

    # 2. Arda Güler'i Ekle
    arda = session.query(Player).filter_by(known_as="Arda Guler").first()
    if not arda:
        arda = Player(
            first_name="Arda",
            last_name="Guler",
            known_as="Arda Guler",
            nationality="Turkey",
            position="Midfielder"
        )
        session.add(arda)
        session.commit()
        
        # Kariyer Yolu: Fenerbahce -> Real Madrid
        h1 = PlayerTeamHistory(player_id=arda.id, team_id=fenerbahce.id, start_year=2021, end_year=2023, is_active=False)
        h2 = PlayerTeamHistory(player_id=arda.id, team_id=rm_team.id, start_year=2023, end_year=None, is_active=True)
        session.add_all([h1, h2])
        session.commit()
        print("Oyuncu ve kariyer geçmişi eklendi: Arda Guler")

    # 3. Toni Kroos'u Ekle
    kroos = session.query(Player).filter_by(known_as="Toni Kroos").first()
    if not kroos:
        kroos = Player(
            first_name="Toni",
            last_name="Kroos",
            known_as="Toni Kroos",
            nationality="Germany",
            position="Midfielder"
        )
        session.add(kroos)
        session.commit()
        
        # Kariyer Yolu: Bayern Munich -> Real Madrid
        h3 = PlayerTeamHistory(player_id=kroos.id, team_id=bayern.id, start_year=2007, end_year=2014, is_active=False)
        h4 = PlayerTeamHistory(player_id=kroos.id, team_id=rm_team.id, start_year=2014, end_year=2024, is_active=False)
        session.add_all([h3, h4])
        session.commit()
        print("Oyuncu ve kariyer geçmişi eklendi: Toni Kroos")

if __name__ == "__main__":
    # Gerçek projede burada BeautifulSoup ile Wikipedia'dan veri parse eden mantık yer alacaktır.
    # Şimdilik "PlayerTeamHistory" mantığını kanıtlamak için Mock Data (Örnek Veri) basıyoruz.
    seed_initial_data()
    print("Veri ekleme (Seeding) tamamlandı.")
