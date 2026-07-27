"""
players tablosuna peak_market_value (Float), current_team_id (Integer) ve
market_value_updated (DateTime) kolonlarini ekler.

peak_market_value, TMAPI'nin marketValueDetails.HIGHEST alanindan gelir
(kariyer zirvesi), "current" degil — emekli/yaslanan oyuncularda "current"
0'a dusuyor ve tanınırlık icin yanıltıcı oluyor (bkz. commit mesaji).

Idempotent'tir: kolonlar zaten varsa dokunmaz; eski (v1) calistirmadan
kalma "market_value" kolonu varsa "peak_market_value"a yeniden adlandirir.
Postgres 9.6+ gerektirir.

Kullanim:
    cd backend && venv\\Scripts\\python.exe scripts/add_player_market_value_columns.py
"""
import os
import sys

from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine


def run():
    with engine.begin() as conn:
        conn.execute(text("""
            DO $$
            BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='players' AND column_name='market_value')
                   AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='players' AND column_name='peak_market_value') THEN
                    ALTER TABLE players RENAME COLUMN market_value TO peak_market_value;
                END IF;
            END $$;
        """))
        conn.execute(text("ALTER TABLE players ADD COLUMN IF NOT EXISTS peak_market_value FLOAT"))
        conn.execute(text("ALTER TABLE players ADD COLUMN IF NOT EXISTS current_team_id INTEGER"))
        conn.execute(text("ALTER TABLE players ADD COLUMN IF NOT EXISTS market_value_updated TIMESTAMP"))
    print("players.peak_market_value / current_team_id / market_value_updated kolonlari hazir.")


if __name__ == "__main__":
    run()
