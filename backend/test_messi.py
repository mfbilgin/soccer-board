import os
from sqlalchemy import create_engine, text

def test_messi():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.connect() as conn:
        player = conn.execute(text("SELECT id, name FROM players WHERE known_as LIKE '%Messi%' LIMIT 1")).fetchone()
        if not player:
            print("Messi not found!")
            return
            
        player_id = player[0]
        player_name = player[1]
        
        # Club Stats for Penalties
        stats = conn.execute(text("SELECT SUM(penalty_goals), SUM(penalty_misses) FROM player_club_stats WHERE player_id = :p"), {'p': player_id}).fetchone()
        
        pen_goals = stats[0] or 0
        pen_misses = stats[1] or 0
        total_pens = pen_goals + pen_misses
        
        success_rate = (pen_goals / total_pens * 100) if total_pens > 0 else 0
        
        print(f"--- {player_name} CLUB CAREER PENALTIES ---")
        print(f"Kullanılan Penaltı: {total_pens}")
        print(f"Atılan Gol: {pen_goals}")
        print(f"Kaçan Penaltı: {pen_misses}")
        print(f"Başarı Oranı: %{success_rate:.1f}")

if __name__ == "__main__":
    test_messi()
