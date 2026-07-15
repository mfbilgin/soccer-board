import os
from sqlalchemy import create_engine, text

def list_messi_shirts():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        player = conn.execute(text("SELECT id, name FROM players WHERE known_as LIKE '%Messi%' LIMIT 1")).fetchone()
        if not player:
            print("Messi not found!")
            return
            
        player_id = player[0]
        player_name = player[1]
        
        # We group by season and team to avoid seeing the same shirt number 4 times for League, Cup, CL etc.
        query = text("""
            SELECT season, t.name, shirt_number 
            FROM player_club_stats pcs
            JOIN teams t ON t.id = pcs.team_id
            WHERE player_id = :p AND shirt_number IS NOT NULL AND shirt_number != 0
            GROUP BY season, t.name, shirt_number
            ORDER BY season ASC
        """)
        
        results = conn.execute(query, {'p': player_id}).fetchall()
        
        print(f"--- {player_name} Forma Numarasi Gecmisi ---")
        for r in results:
            print(f"Sezon: {r[0]} | Takim: {r[1]} | Forma: {r[2]}")

if __name__ == "__main__":
    list_messi_shirts()
