"""
players tablosuna height_cm (Integer, nullable) kolonunu ekler.

Idempotent'tir: kolon zaten varsa IF NOT EXISTS sayesinde no-op olur, tekrar
calistirmak guvenlidir. Postgres 9.6+ gerektirir (ADD COLUMN IF NOT EXISTS).

Kullanim:
    cd backend && venv\\Scripts\\python.exe scripts/add_height_cm_column.py
"""
import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine


def run():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE players ADD COLUMN IF NOT EXISTS height_cm INTEGER"))
    print("players.height_cm kolonu hazir (zaten vardiysa dokunulmadi).")


if __name__ == "__main__":
    run()
