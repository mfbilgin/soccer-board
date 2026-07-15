import os
from sqlalchemy import create_engine, text

db_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
engine = create_engine(db_url)

with engine.connect() as conn:
    olise = conn.execute(text("SELECT id, api_id, name FROM players WHERE name ILIKE '%Michael Olise%'")).fetchone()
    print("Olise DB ID:", olise.id, "API ID:", olise.api_id)
