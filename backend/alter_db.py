import os
from sqlalchemy import create_engine
from sqlalchemy import text

def alter_db():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.begin() as conn:
        print("Adding columns to player_club_stats...")
        try:
            conn.execute(text("ALTER TABLE player_club_stats ADD COLUMN started_matches INTEGER DEFAULT 0;"))
        except Exception as e:
            print(e)
            
        try:
            conn.execute(text("ALTER TABLE player_club_stats ADD COLUMN penalty_goals INTEGER DEFAULT 0;"))
        except Exception as e:
            print(e)
            
        try:
            conn.execute(text("ALTER TABLE player_club_stats ADD COLUMN penalty_misses INTEGER DEFAULT 0;"))
        except Exception as e:
            print(e)
            
        try:
            conn.execute(text("ALTER TABLE player_club_stats ADD COLUMN shirt_number INTEGER;"))
        except Exception as e:
            print(e)

        print("Adding columns to player_transfers...")
        try:
            conn.execute(text("ALTER TABLE player_transfers ADD COLUMN market_value VARCHAR;"))
        except Exception as e:
            print(e)
            
    print("Alter table commands completed.")

if __name__ == "__main__":
    alter_db()
