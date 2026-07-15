import os
from sqlalchemy import create_engine, text

db_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
engine = create_engine(db_url)

with engine.connect() as conn:
    mid = conn.execute(text("SELECT id FROM players WHERE name ILIKE '%Lionel Messi%'")).scalar()
    club_mins = conn.execute(text(f"SELECT SUM(minutes_played) FROM player_club_stats WHERE player_id = {mid}")).scalar()
    print(f"Messi ID: {mid}, Club Mins: {club_mins}")
