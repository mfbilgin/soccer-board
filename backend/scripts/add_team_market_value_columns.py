"""
teams tablosuna market_value (Float), primary_competition_id (String) ve
market_value_updated (DateTime) kolonlarini ekler.

Idempotent'tir: kolonlar zaten varsa IF NOT EXISTS sayesinde no-op olur,
tekrar calistirmak guvenlidir. Postgres 9.6+ gerektirir.

Kullanim:
    cd backend && venv\\Scripts\\python.exe scripts/add_team_market_value_columns.py
"""
import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine


def run():
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS market_value FLOAT"))
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS primary_competition_id VARCHAR"))
        conn.execute(text("ALTER TABLE teams ADD COLUMN IF NOT EXISTS market_value_updated TIMESTAMP"))
    print("teams.market_value / primary_competition_id / market_value_updated kolonlari hazir.")


if __name__ == "__main__":
    run()
