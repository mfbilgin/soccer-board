import os
from sqlalchemy import create_engine, text

def test_etoo():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        player = conn.execute(text("SELECT id, name FROM players WHERE known_as LIKE '%Eto''o%' OR name LIKE '%Eto''o%' LIMIT 1")).fetchone()
        if not player:
            print("Samuel Eto'o not found!")
            return
            
        player_id = player[0]
        player_name = player[1]
        
        # Barcelona Stats
        barca_team = conn.execute(text("SELECT id FROM teams WHERE name LIKE '%Barcelona%' LIMIT 1")).scalar()
        if barca_team:
            barca_stats = conn.execute(text("SELECT SUM(goals), SUM(appearances), SUM(assists) FROM player_club_stats WHERE player_id = :p AND team_id = :t"), {'p': player_id, 't': barca_team}).fetchone()
            print(f"--- {player_name} in FC Barcelona ---")
            print(f"Maç: {barca_stats[1]}, Gol: {barca_stats[0]}, Asist: {barca_stats[2]}")
            
        # Inter Stats
        inter_team = conn.execute(text("SELECT id FROM teams WHERE name LIKE '%Inter%' LIMIT 1")).scalar()
        if inter_team:
            inter_stats = conn.execute(text("SELECT SUM(goals), SUM(appearances), SUM(assists) FROM player_club_stats WHERE player_id = :p AND team_id = :t"), {'p': player_id, 't': inter_team}).fetchone()
            print(f"\n--- {player_name} in Inter ---")
            print(f"Maç: {inter_stats[1]}, Gol: {inter_stats[0]}, Asist: {inter_stats[2]}")

        # Total Career Club Stats
        total_stats = conn.execute(text("SELECT SUM(goals), SUM(appearances), SUM(assists) FROM player_club_stats WHERE player_id = :p"), {'p': player_id}).fetchone()
        print(f"\n--- {player_name} TOTAL CLUB CAREER ---")
        print(f"Maç: {total_stats[1]}, Gol: {total_stats[0]}, Asist: {total_stats[2]}")
        
        # National Stats
        nat_stats = conn.execute(text("SELECT SUM(goals), SUM(caps), SUM(assists) FROM player_national_stats WHERE player_id = :p"), {'p': player_id}).fetchone()
        if nat_stats and nat_stats[0] is not None:
            print(f"\n--- {player_name} NATIONAL TEAM ---")
            print(f"Maç: {nat_stats[1]}, Gol: {nat_stats[0]}, Asist: {nat_stats[2]}")

if __name__ == "__main__":
    test_etoo()
