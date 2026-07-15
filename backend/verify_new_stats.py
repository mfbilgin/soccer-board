import os
from sqlalchemy import create_engine, text

def verify():
    db_url = os.getenv("DATABASE_URL_V2")
    if not db_url:
        print("DATABASE_URL_V2 is not set.")
        return
        
    engine = create_engine(db_url)
    with engine.connect() as conn:
        print("=== DATABASE COUNTS ===")
        
        club_count = conn.execute(text("SELECT COUNT(*) FROM player_club_stats")).scalar()
        nat_count = conn.execute(text("SELECT COUNT(*) FROM player_national_stats")).scalar()
        trans_count = conn.execute(text("SELECT COUNT(*) FROM player_transfers")).scalar()
        
        print(f"Club Stats Rows: {club_count}")
        print(f"National Stats Rows: {nat_count}")
        print(f"Transfers Rows: {trans_count}")
        
        print("\n=== SAMPLE CLUB STAT (Checking new columns) ===")
        sample_club = conn.execute(text("SELECT * FROM player_club_stats LIMIT 1")).fetchone()
        if sample_club:
            cols = sample_club._mapping.keys()
            for col in cols:
                print(f"  {col}: {sample_club._mapping[col]}")
        else:
            print("  No club stats yet.")
            
        print("\n=== SAMPLE TRANSFER (Checking new columns) ===")
        sample_trans = conn.execute(text("SELECT * FROM player_transfers LIMIT 1")).fetchone()
        if sample_trans:
            cols = sample_trans._mapping.keys()
            for col in cols:
                print(f"  {col}: {sample_trans._mapping[col]}")
        else:
            print("  No transfers yet.")

if __name__ == "__main__":
    verify()
