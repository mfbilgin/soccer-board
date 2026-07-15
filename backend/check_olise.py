import os
from sqlalchemy import create_engine, text

db_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
engine = create_engine(db_url)

with engine.connect() as conn:
    olise = conn.execute(text("SELECT id, name FROM players WHERE name ILIKE '%Michael Olise%'")).fetchone()
    if olise:
        query = text("""
            SELECT s.season, c.name as comp, s.appearances, s.goals, s.assists
            FROM player_club_stats s
            JOIN competitions c ON s.competition_id = c.id
            WHERE s.player_id = :pid AND c.name = 'L1'
        """)
        stats = conn.execute(query, {"pid": olise.id}).fetchall()
        for s in stats:
            print(s)
