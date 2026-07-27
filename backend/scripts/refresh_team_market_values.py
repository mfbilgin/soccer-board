"""
Appearances'a gore en cok forma giyilen N takimin TMAPI'den guncel kadro
piyasa degerini (currentMarketValue) ve guncel lig kimligini
(primaryCompetitionId) ceker, teams.market_value / primary_competition_id
kolonlarina yazar.

Idempotent'tir: --force verilmedigi surece son 24 saat icinde guncellenmis
takimlari atlar; kesintiye ugrarsa yeniden calistirmak guvenlidir (her
COMMIT_BATCH_SIZE takimda bir commit edilir).

On kosul: scripts/add_team_market_value_columns.py calistirilmis olmali.

Kullanim:
    cd backend && venv\\Scripts\\python.exe scripts/refresh_team_market_values.py [--limit N] [--force]
"""
import argparse
import os
import sys
import time
from datetime import datetime, timedelta

import requests
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import SessionLocal

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
RATE_LIMIT_SECONDS = 0.6
REFRESH_STALE_AFTER = timedelta(hours=24)
DEFAULT_CANDIDATE_LIMIT = 2000
COMMIT_BATCH_SIZE = 50


def fetch_club_profile(api_id):
    """TMAPI'den kadro piyasa degeri ve guncel lig id'sini ceker. Basarisiz olursa None doner."""
    try:
        resp = requests.get(f"{TMAPI_BASE}/club/{api_id}", headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        data = (resp.json() or {}).get("data") or {}
        if not data or data.get("isSpecialClub"):
            return None
        market_value = ((data.get("squadDetails") or {}).get("currentMarketValue") or {}).get("value")
        primary_comp = (data.get("baseDetails") or {}).get("primaryCompetitionId")
        return {"market_value": market_value, "primary_competition_id": primary_comp}
    except Exception:
        return None


def get_candidate_team_ids(db, limit):
    """Appearances toplamina gore en cok forma giyilen `limit` takimin id'lerini dondurur."""
    rows = (
        db.query(models.PlayerClubStat.team_id)
        .group_by(models.PlayerClubStat.team_id)
        .order_by(func.sum(models.PlayerClubStat.appearances).desc())
        .limit(limit)
        .all()
    )
    return [r[0] for r in rows]


def run(limit: int, force: bool):
    db = SessionLocal()
    try:
        candidate_ids = get_candidate_team_ids(db, limit)
        teams = db.query(models.Team.id, models.Team.api_id, models.Team.market_value_updated) \
            .filter(models.Team.id.in_(candidate_ids)).all()

        if not force:
            cutoff = datetime.utcnow() - REFRESH_STALE_AFTER
            teams = [t for t in teams if not t.market_value_updated or t.market_value_updated < cutoff]
    finally:
        db.close()

    total = len(teams)
    print(f"{total} takim taranacak (aday havuzu: {len(candidate_ids)}, force={force}).")

    updated = 0
    failed = 0
    db = SessionLocal()
    try:
        for i, (team_id, api_id, _) in enumerate(teams, start=1):
            profile = fetch_club_profile(api_id)

            try:
                if profile and profile["market_value"] is not None:
                    db.query(models.Team).filter(models.Team.id == team_id).update({
                        "market_value": profile["market_value"],
                        "primary_competition_id": profile["primary_competition_id"],
                        "market_value_updated": datetime.utcnow(),
                    })
                    updated += 1
                else:
                    failed += 1

                if i % COMMIT_BATCH_SIZE == 0:
                    db.commit()
                    print(f"  [{i}/{total}] islendi, {updated} guncellendi, {failed} basarisiz...")
            except Exception as e:
                # Gecici DB baglanti sorunlari (ör. "server closed the connection
                # unexpectedly") tum taramayi durdurmasin: oturumu tazele, bu
                # takimi basarisiz say, devam et. Idempotent tasarim sayesinde
                # script yeniden calistirilinca zaten atlanmis olan bu takim
                # tekrar denenir.
                print(f"  [{i}/{total}] HATA (team_id={team_id}): {e}")
                db.rollback()
                db.close()
                db = SessionLocal()
                failed += 1

            time.sleep(RATE_LIMIT_SECONDS)

        db.commit()
        print(f"Bitti. {updated} takim guncellendi, {failed} takim basarisiz/veri yok.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=DEFAULT_CANDIDATE_LIMIT, help="Appearances'a gore taranacak aday takim sayisi")
    parser.add_argument("--force", action="store_true", help="Son 24 saatte guncellenmis takimlari da yeniden tara")
    args = parser.parse_args()
    run(args.limit, args.force)
