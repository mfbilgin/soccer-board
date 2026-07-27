from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL_V2")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL_V2 ortam degiskeni tanimli degil. "
        "backend/.env.example dosyasina bakip yerel .env dosyani olustur "
        "(prod calisiyorsa deploy platformunda da bu degiskenin tanimli oldugundan emin ol)."
    )

# SQLite uses check_same_thread, Postgres doesn't
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # kullanmadan once baglantiyi "ping"ler; yonetilen DB'nin
                          # boşta kalan baglantilari sessizce kapatmasina karsi
                          # (bkz. "server closed the connection unexpectedly")
    pool_recycle=280,    # yaygin managed-DB idle-timeout esiklerinden (~300sn)
                          # once baglantiyi proaktif olarak tazeler
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
