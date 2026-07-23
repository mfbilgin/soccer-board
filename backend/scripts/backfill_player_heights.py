"""
height_cm IS NULL olan oyunculari TMAPI'nin /player/{api_id} profil uc
noktasindan gelen attributes.height (metre) degeriyle doldurur.

Idempotent'tir: yalnizca hala height_cm IS NULL olan satirlari hedefler, bu
yuzden guvenle kesilip devam ettirilebilir veya ileride tekrar calistirilabilir.

Kullanim:
    cd backend && venv\\Scripts\\python.exe scripts/backfill_player_heights.py --limit 20   # test batch
    cd backend && venv\\Scripts\\python.exe scripts/backfill_player_heights.py               # tam calistirma
"""
import argparse
import os
import sys
import time

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Player

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}


def fetch_height_cm(api_id):
    try:
        resp = requests.get(f"{TMAPI_BASE}/player/{api_id}", headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        payload = resp.json()
    except Exception:
        return None

    data = payload.get('data', {}) or {}
    height_m = (data.get('attributes', {}) or {}).get('height')
    if not height_m:
        return None
    return round(height_m * 100)


def run(limit=None, batch_size=200):
    db = SessionLocal()
    try:
        query = db.query(Player).filter(Player.height_cm.is_(None)).order_by(Player.id)
        if limit:
            query = query.limit(limit)
        broken = query.all()
        print(f"{len(broken)} oyuncu islenecek.")

        updated, failed = 0, 0
        for i, player in enumerate(broken):
            height_cm = fetch_height_cm(player.api_id)
            time.sleep(0.5)
            if height_cm:
                player.height_cm = height_cm
                updated += 1
            else:
                failed += 1

            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"  {i + 1}/{len(broken)} islendi ({updated} guncellendi, {failed} basarisiz)")

        db.commit()
        print(f"Bitti. {updated} guncellendi, {failed} basarisiz (TMAPI'den veri gelmedi).")

        remaining = db.query(Player).filter(Player.height_cm.is_(None)).count()
        print(f"Hala height_cm eksik olan oyuncu sayisi: {remaining}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Test icin ilk N satiri isle")
    args = parser.parse_args()
    run(limit=args.limit)
