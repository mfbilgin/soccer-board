from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL_V2", 
    "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
)

# SQLite uses check_same_thread, Postgres doesn't
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
