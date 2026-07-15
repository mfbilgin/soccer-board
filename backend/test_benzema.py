import os
from sqlalchemy import create_engine, text

def test_benzema():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        player = conn.execute(text("SELECT id FROM players WHERE known_as LIKE '%Benzema%' LIMIT 1")).scalar()
        team = conn.execute(text("SELECT id FROM teams WHERE name LIKE '%Real Madrid%' LIMIT 1")).scalar()
        
        if player and team:
            stats = conn.execute(text("SELECT SUM(goals), SUM(appearances), SUM(assists) FROM player_club_stats WHERE player_id = :p AND team_id = :t"), {'p': player, 't': team}).fetchone()
            print(f"Maç: {stats[1]}, Gol: {stats[0]}, Asist: {stats[2]}")
        else:
            print("Not found")

if __name__ == "__main__":
    test_benzema()
