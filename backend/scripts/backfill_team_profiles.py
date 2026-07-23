"""
Placeholder isimli ("Team 12345") ve/veya ulke bilgisi eksik (country IS NULL)
takimlari TMAPI'nin /club/{api_id} profil uc noktasindan gelen kanonik veriyle
onarir: name, short_name (Transfermarkt'in kendi resmi kisa ismi), country ve type.

Idempotent'tir: yalnizca hala bozuk olan satirlari hedefler (name ~ '^Team \\d+$'
OR country IS NULL), bu yuzden guvenle kesilip devam ettirilebilir veya ileride
tekrar calistirilabilir.

Hangi veritabanina yazacagi backend/.env icindeki DATABASE_URL_V2'ye baglidir
(bkz. backend/.env.example). Production Postgres'e yazmadan once o degerin
dogru oldugundan emin ol.

Kullanim:
    cd backend && ..\\venv\\Scripts\\python.exe scripts/backfill_team_profiles.py --limit 20   # test batch
    cd backend && ..\\venv\\Scripts\\python.exe scripts/backfill_team_profiles.py               # tam calistirma
"""
import argparse
import csv
import os
import re
import sys
import time

import requests
from sqlalchemy import or_, text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Team

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
PLACEHOLDER_NAME_RE = r'^Team \d+$'


def _load_country_map():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'countries.csv')
    m = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            m[int(row['country_id'])] = row['country_name']
    return m


COUNTRY_BY_ID = _load_country_map()


def fetch_profile(api_id):
    try:
        resp = requests.get(f"{TMAPI_BASE}/club/{api_id}", headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        payload = resp.json()
    except Exception:
        return None

    data = payload.get('data', {}) or {}
    if not data:
        return None
    base = data.get('baseDetails', {}) or {}
    country_id = base.get('countryId')
    return {
        "name": data.get('name'),
        "short_name": base.get('shortName') or base.get('abbreviation'),
        "country": COUNTRY_BY_ID.get(country_id) if country_id else None,
        "type": 'national' if base.get('isNationalTeam') else 'club',
    }


def run(limit=None, batch_size=200):
    db = SessionLocal()
    try:
        query = db.query(Team).filter(
            or_(Team.name.op('~')(PLACEHOLDER_NAME_RE), Team.country.is_(None))
        ).order_by(Team.id)
        if limit:
            query = query.limit(limit)
        broken = query.all()
        print(f"{len(broken)} takim islenecek.")

        updated, failed = 0, 0
        for i, team in enumerate(broken):
            profile = fetch_profile(team.api_id)
            time.sleep(0.5)
            if profile:
                if profile['name']:
                    team.name = profile['name']
                if profile['short_name']:
                    team.short_name = profile['short_name']
                if profile['country']:
                    team.country = profile['country']
                if profile['type']:
                    team.type = profile['type']
                updated += 1
            else:
                failed += 1

            if (i + 1) % batch_size == 0:
                db.commit()
                print(f"  {i + 1}/{len(broken)} islendi ({updated} guncellendi, {failed} basarisiz)")

        db.commit()
        print(f"Bitti. {updated} guncellendi, {failed} basarisiz (TMAPI'den veri gelmedi).")

        remaining = db.query(Team).filter(
            or_(Team.name.op('~')(PLACEHOLDER_NAME_RE), Team.country.is_(None))
        ).count()
        print(f"Hala eksik olan takim sayisi: {remaining}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Test icin ilk N satiri isle")
    args = parser.parse_args()
    run(limit=args.limit)
