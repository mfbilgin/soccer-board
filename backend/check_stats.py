import os
from sqlalchemy import create_engine, text

db_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
engine = create_engine(db_url)

with engine.connect() as conn:
    olise = conn.execute(text("SELECT id, name FROM players WHERE name ILIKE '%Michael Olise%'")).fetchone()
    diaz = conn.execute(text("SELECT id, name FROM players WHERE name ILIKE '%Luis Díaz%' OR name ILIKE '%Luis Diaz%'")).fetchone()

    for p in [olise, diaz]:
        if p:
            print(f"\n--- {p.name} (ID: {p.id}) ---")
            query = text("""
                SELECT c.name, SUM(s.appearances), SUM(s.goals), SUM(s.assists)
                FROM player_club_stats s
                JOIN competitions c ON s.competition_id = c.id
                WHERE s.player_id = :pid
                GROUP BY c.name
                ORDER BY SUM(s.appearances) DESC
            """)
            stats = conn.execute(query, {"pid": p.id}).fetchall()
            for s in stats:
                print(f"{s[0]}: {s[1]} Maç, {s[2]} Gol, {s[3]} Asist")
        else:
            print("\nPlayer not found.")
