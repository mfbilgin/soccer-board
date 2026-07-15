import os
from sqlalchemy import create_engine, text

db_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
engine = create_engine(db_url)

with engine.connect() as conn:
    olise = conn.execute(text("SELECT id FROM players WHERE name ILIKE '%Michael Olise%'")).fetchone()
    if olise:
        query = text("""
            SELECT s.season, s.competition_id, s.appearances, s.goals, s.assists
            FROM player_club_stats s
            WHERE s.player_id = :pid AND s.season IN ('2024', '2025')
            ORDER BY s.season, s.competition_id
        """)
        stats = conn.execute(query, {"pid": olise.id}).fetchall()
        for s in stats:
            print(s)
