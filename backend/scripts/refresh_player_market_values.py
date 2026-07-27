"""
Aday oyuncu evreni appearances toplamına göre değil (genç süperstarlar —
Haaland, Mbappé, Vinicius Jr — appearances'ta binlerce sırada geriden
başlıyor, top-2000'e hiç girmiyorlar), kariyerinde en az MIN_APPEARANCES
maç bizim tanınır-takım havuzumuzdaki (tictactoe.PER_COMPETITION_LIMIT,
Big-5 + Süper Lig) bir kulüpte oynamış olmasına göre belirlenir. Bu bilgi
zaten PlayerClubStat'ta var, TMAPI'ye gitmeden hesaplanır.

Her aday için TMAPI'den marketValueDetails.HIGHEST (kariyer zirvesi —
"current" emekli/yaşlanan oyuncularda 0'a düşüyor, tanınırlık için
yanıltıcı) ve clubAssignments[type=current].clubId (bonus veri, gelecekte
kullanılabilir) çekilir. peak_market_value = max(TMAPI highest, DB'deki
PlayerTransfer.market_value kayıtlarının ayrıştırılmış en yükseği) —
ikincisi bazı oyuncularda (özellikle uzun süre tek kulüpte kalanlar için
TMAPI'nin "highest"i eksik/düşük kalırsa) ek bir güvenlik sağlar.

Idempotent'tir: --force verilmedigi surece son 24 saat icinde guncellenmis
oyunculari atlar; kesintiye ugrarsa yeniden calistirmak guvenlidir (her
COMMIT_BATCH_SIZE oyuncuda bir commit edilir).

On kosul: scripts/add_player_market_value_columns.py calistirilmis olmali.

Kullanim:
    cd backend && venv\\Scripts\\python.exe scripts/refresh_player_market_values.py [--limit N] [--force]
"""
import argparse
import os
import re
import sys
import time
from datetime import datetime, timedelta

import requests
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models
from database import SessionLocal
from tictactoe import PER_COMPETITION_LIMIT

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
RATE_LIMIT_SECONDS = 0.6
REFRESH_STALE_AFTER = timedelta(hours=24)
MIN_APPEARANCES = 10
COMMIT_BATCH_SIZE = 50

TRANSFER_VALUE_RE = re.compile(r'^([\d]+(?:[.,]\d+)?)\s*(mil\.?|bin)?')


def parse_turkish_market_value(raw: str):
    """PlayerTransfer.market_value gibi Turkce formatli metni (ör. '6.00 mil. €',
    '500 bin €') EUR sayisina cevirir. Ayristirilamayan/degersiz metinlerde
    ('-', 'Bedelsiz', 'Kiralik' vb.) None doner."""
    if not raw:
        return None
    raw = raw.strip()
    if raw in ('-', '?') or 'Bedelsiz' in raw or 'Kiral' in raw:
        return None
    m = TRANSFER_VALUE_RE.match(raw)
    if not m:
        return None
    try:
        num = float(m.group(1).replace(',', '.'))
    except ValueError:
        return None
    unit = m.group(2)
    if unit and unit.startswith('mil'):
        return num * 1_000_000
    if unit == 'bin':
        return num * 1_000
    return num


def get_recognizable_team_ids(db):
    """tictactoe.TicTacToeEngine._select_popular_teams ile ayni mantik:
    Big-5+TR1 ligindeki takimlari lig basina PER_COMPETITION_LIMIT'e gore
    market_value siralayip secer (tam TicTacToeEngine'i ayaga kaldirmadan,
    hafif bir sekilde)."""
    rows = db.query(models.Team.id, models.Team.market_value, models.Team.primary_competition_id) \
        .filter(models.Team.primary_competition_id.in_(PER_COMPETITION_LIMIT.keys())) \
        .all()

    by_competition = {}
    for tid, mv, comp in rows:
        by_competition.setdefault(comp, []).append((tid, mv))

    team_ids = []
    for comp, limit in PER_COMPETITION_LIMIT.items():
        teams = by_competition.get(comp, [])
        with_value = sorted([(tid, mv) for tid, mv in teams if mv is not None], key=lambda x: x[1], reverse=True)
        team_ids += [tid for tid, _ in with_value[:limit]]

    return team_ids


def fetch_player_profile(api_id):
    """TMAPI'den kariyer zirvesi piyasa degerini ve su anki kulup id'sini ceker. Basarisiz olursa None doner."""
    try:
        resp = requests.get(f"{TMAPI_BASE}/player/{api_id}", headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None
        data = (resp.json() or {}).get("data") or {}
        if not data:
            return None
        peak_value = ((data.get("marketValueDetails") or {}).get("highest") or {}).get("value")
        current_club_id = None
        for assignment in data.get("clubAssignments") or []:
            if assignment.get("type") == "current":
                current_club_id = assignment.get("clubId")
                break
        return {"peak_market_value": peak_value, "current_club_api_id": current_club_id}
    except Exception:
        return None


def get_candidate_player_ids(db, team_ids, limit=None):
    """Kariyerinde en az MIN_APPEARANCES mac bu takimlardan birinde oynamis
    oyuncularin id'lerini, toplam appearances'a gore sirali dondurur."""
    query = db.query(models.PlayerClubStat.player_id) \
        .filter(models.PlayerClubStat.team_id.in_(team_ids)) \
        .group_by(models.PlayerClubStat.player_id) \
        .having(func.sum(models.PlayerClubStat.appearances) >= MIN_APPEARANCES) \
        .order_by(func.sum(models.PlayerClubStat.appearances).desc())
    if limit:
        query = query.limit(limit)
    return [r[0] for r in query.all()]


def get_transfer_market_value_max(db, player_ids):
    """Her oyuncu icin PlayerTransfer.market_value kayitlarinin ayristirilmis
    en yuksegini dondurur (peak_market_value icin ikincil/guvenlik sinyali)."""
    rows = db.query(models.PlayerTransfer.player_id, models.PlayerTransfer.market_value) \
        .filter(models.PlayerTransfer.player_id.in_(player_ids)) \
        .all()
    max_by_player = {}
    for pid, raw in rows:
        value = parse_turkish_market_value(raw)
        if value is None:
            continue
        if value > max_by_player.get(pid, 0):
            max_by_player[pid] = value
    return max_by_player


def run(limit: int, force: bool):
    db = SessionLocal()
    try:
        team_ids = get_recognizable_team_ids(db)
        print(f"Taninir takim havuzu: {len(team_ids)} takim.")

        candidate_ids = get_candidate_player_ids(db, team_ids, limit)
        players = db.query(models.Player.id, models.Player.api_id, models.Player.market_value_updated) \
            .filter(models.Player.id.in_(candidate_ids)).all()

        if not force:
            cutoff = datetime.utcnow() - REFRESH_STALE_AFTER
            players = [p for p in players if not p.market_value_updated or p.market_value_updated < cutoff]

        transfer_value_max = get_transfer_market_value_max(db, [p.id for p in players])

        team_api_id_to_id = {api_id: tid for tid, api_id in db.query(models.Team.id, models.Team.api_id).all()}
    finally:
        db.close()

    total = len(players)
    print(f"{total} oyuncu taranacak (aday havuzu: {len(candidate_ids)}, min_appearances={MIN_APPEARANCES}, force={force}).")

    updated = 0
    failed = 0
    db = SessionLocal()
    try:
        for i, (player_id, api_id, _) in enumerate(players, start=1):
            profile = fetch_player_profile(api_id)

            try:
                tmapi_peak = profile["peak_market_value"] if profile else None
                transfer_peak = transfer_value_max.get(player_id)
                candidates = [v for v in (tmapi_peak, transfer_peak) if v is not None]
                final_peak = max(candidates) if candidates else None

                if final_peak is not None:
                    current_club_api_id = profile.get("current_club_api_id") if profile else None
                    current_team_id = None
                    if current_club_api_id is not None:
                        try:
                            current_team_id = team_api_id_to_id.get(int(current_club_api_id))
                        except (TypeError, ValueError):
                            current_team_id = None

                    db.query(models.Player).filter(models.Player.id == player_id).update({
                        "peak_market_value": final_peak,
                        "current_team_id": current_team_id,
                        "market_value_updated": datetime.utcnow(),
                    })
                    updated += 1
                else:
                    failed += 1

                if i % COMMIT_BATCH_SIZE == 0:
                    db.commit()
                    print(f"  [{i}/{total}] islendi, {updated} guncellendi, {failed} basarisiz...")
            except Exception as e:
                print(f"  [{i}/{total}] HATA (player_id={player_id}): {e}")
                db.rollback()
                db.close()
                db = SessionLocal()
                failed += 1

            time.sleep(RATE_LIMIT_SECONDS)

        db.commit()
        print(f"Bitti. {updated} oyuncu guncellendi, {failed} oyuncu basarisiz/veri yok.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Taranacak aday oyuncu sayisini sinirla (test icin)")
    parser.add_argument("--force", action="store_true", help="Son 24 saatte guncellenmis oyunculari da yeniden tara")
    args = parser.parse_args()
    run(args.limit, args.force)
