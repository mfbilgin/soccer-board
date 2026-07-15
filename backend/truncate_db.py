import os
from sqlalchemy import create_engine, text

def truncate():
    db_url = os.getenv("DATABASE_URL_V2")
    if not db_url:
        print("DATABASE_URL_V2 is not set.")
        return
        
    engine = create_engine(db_url)
    with engine.begin() as conn:
        print("Truncating stats tables...")
        conn.execute(text("TRUNCATE TABLE player_club_stats CASCADE;"))
        conn.execute(text("TRUNCATE TABLE player_national_stats CASCADE;"))
        conn.execute(text("TRUNCATE TABLE player_transfers CASCADE;"))
        conn.execute(text("TRUNCATE TABLE player_honours CASCADE;"))
        
        print("Resetting player active status...")
        conn.execute(text("UPDATE players SET is_active = True;"))
        
        print("Querying remaining data...")
        players_count = conn.execute(text("SELECT COUNT(*) FROM players")).scalar()
        teams_count = conn.execute(text("SELECT COUNT(*) FROM teams")).scalar()
        comps_count = conn.execute(text("SELECT COUNT(*) FROM competitions")).scalar()
        
        print(f"REMAINING_PLAYERS: {players_count}")
        print(f"REMAINING_TEAMS: {teams_count}")
        print(f"REMAINING_COMPS: {comps_count}")

if __name__ == "__main__":
    truncate()
