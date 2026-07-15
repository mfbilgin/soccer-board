import os
from sqlalchemy import create_engine, text

def list_morata_transfers():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        # Fetch Morata
        player = conn.execute(text("SELECT id, name, known_as FROM players WHERE known_as LIKE '%Morata%' OR name LIKE '%Morata%' LIMIT 1")).fetchone()
        if not player:
            print("Morata not found!")
            return
            
        player_id = player[0]
        player_name = player[2] or player[1]
        
        query = text("""
            SELECT transfer_date, t_from.name, t_to.name, transfer_fee, market_value
            FROM player_transfers pt
            JOIN teams t_from ON t_from.id = pt.from_team_id
            JOIN teams t_to ON t_to.id = pt.to_team_id
            WHERE player_id = :p
            ORDER BY transfer_date ASC
        """)
        
        results = conn.execute(query, {'p': player_id}).fetchall()
        
        print(f"--- {player_name} Transfer Gecmisi ---")
        for r in results:
            print(f"Tarih: {r[0]} | Nereden: {r[1]:<20} | Nereye: {r[2]:<20} | Bonservis: {r[3]:<15} | Piyasa Degeri: {r[4]}")

if __name__ == "__main__":
    list_morata_transfers()
