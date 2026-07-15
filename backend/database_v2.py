import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# V2 Veritabanı
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL_V2", "sqlite:///./football_trivia_v2.db")

# SQLite için check_same_thread gerekirken, Postgres için gerekmez.
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Postgres
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocalV2 = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_v2():
    db = SessionLocalV2()
    try:
        yield db
    finally:
        db.close()
