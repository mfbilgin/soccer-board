import os
from sqlalchemy import create_engine, text

db_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
engine = create_engine(db_url)

with engine.connect() as conn:
    olise = conn.execute(text("SELECT id, name FROM players WHERE name ILIKE '%Michael Olise%'")).fetchone()
    diaz = conn.execute(text("SELECT id, name FROM players WHERE name ILIKE '%Luis Díaz%' OR name ILIKE '%Luis Diaz%'")).fetchone()

    for p in [olise, diaz]:
        if p:
            print(f"\n--- {p.name} (ID: {p.id}) L1 Stats ---")
            query = text("""
                SELECT s.season, s.club_id, c.name, s.appearances, s.goals, s.assists
                FROM player_club_stats s
                JOIN clubs c ON s.club_id = c.id
                WHERE s.player_id = :pid AND s.competition_id = 'L1'
            """)
            stats = conn.execute(query, {"pid": p.id}).fetchall()
            for s in stats:
                print(s)
