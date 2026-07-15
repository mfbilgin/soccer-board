import os
from sqlalchemy import create_engine, text

def list_messi_market():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        player = conn.execute(text("SELECT id, name FROM players WHERE known_as LIKE '%Messi%' LIMIT 1")).fetchone()
        if not player:
            print("Messi not found!")
            return
            
        player_id = player[0]
        player_name = player[1]
        
        query = text("""
            SELECT transfer_date, t_to.name, market_value, transfer_fee
            FROM player_transfers pt
            JOIN teams t_to ON t_to.id = pt.to_team_id
            WHERE player_id = :p
            ORDER BY transfer_date ASC
        """)
        
        results = conn.execute(query, {'p': player_id}).fetchall()
        
        print(f"--- {player_name} Transfer & Piyasa Degeri Gecmisi ---")
        for r in results:
            print(f"Tarih: {r[0]} | Gittigi Takim: {r[1]} | Piyasa Degeri: {r[2]} | Bonservis: {r[3]}")

if __name__ == "__main__":
    list_messi_market()
