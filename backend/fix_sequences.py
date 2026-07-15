import os
from sqlalchemy import create_engine
from sqlalchemy import text

def fix_sequences():
    db_url = os.getenv("DATABASE_URL_V2")
    engine = create_engine(db_url)
    with engine.begin() as conn:
        try:
            # PostgreSQL'de manuel id eklenince sequence bozulur. Onu düzeltiyoruz.
            conn.execute(text("SELECT setval('teams_id_seq', COALESCE((SELECT MAX(id)+1 FROM teams), 1), false);"))
            conn.execute(text("SELECT setval('players_id_seq', COALESCE((SELECT MAX(id)+1 FROM players), 1), false);"))
            # Diğer tablolar için de her ihtimale karşı:
            conn.execute(text("SELECT setval('competitions_id_seq', COALESCE((SELECT MAX(id)+1 FROM competitions), 1), false);"))
            print("Sequences fixed successfully!")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    fix_sequences()
