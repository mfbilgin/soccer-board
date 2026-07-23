from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
import uuid
from datetime import date

import models
from database import get_db
from routers.auth import get_current_user
from services.economy import add_xp_and_check_level

router = APIRouter(prefix="/api/games/extreme-squad", tags=["Extreme Squad"])

SLOT_ROLES = ["Goalkeeper", "Defender", "Defender", "Defender", "Defender", "Midfield", "Midfield", "Midfield", "Attack", "Attack", "Attack"]
SLOT_ROLE_SET = set(SLOT_ROLES)


def _age_years(birth_date_str: str, today: date) -> int:
    # birth_date "YYYY-MM-DD" veya "YYYY-MM-DD HH:MM:SS" olarak saklanabiliyor
    y, m, d = map(int, birth_date_str.split(" ")[0].split("-"))
    return today.year - y - ((today.month, today.day) < (m, d))


def _build_active_squad_index(db: Session, criterion: str) -> dict:
    """{team_id: {role: [{"id":pid, "value":val, "name":name}, ...]}}

    value = height_cm (tallest) veya yas (youngest). "Su an X takiminda aktif"
    kurali: is_active=true VE en guncel transfer_date'e sahip to_team_id = takim.
    """
    require_height = criterion == "tallest"
    today = date.today()

    latest = db.query(
        models.PlayerTransfer.player_id,
        func.max(models.PlayerTransfer.transfer_date).label("max_date")
    ).group_by(models.PlayerTransfer.player_id).subquery()

    current_team_rows = db.query(
        models.PlayerTransfer.player_id,
        models.PlayerTransfer.to_team_id
    ).join(
        latest,
        (models.PlayerTransfer.player_id == latest.c.player_id) & (models.PlayerTransfer.transfer_date == latest.c.max_date)
    ).all()
    current_team = dict(current_team_rows)

    q = db.query(models.Player).filter(
        models.Player.is_active == True,
        models.Player.position.in_(list(SLOT_ROLE_SET)),
    )
    if require_height:
        q = q.filter(models.Player.height_cm.isnot(None))
    else:
        q = q.filter(models.Player.birth_date.isnot(None))

    index = {}
    for p in q.all():
        team_id = current_team.get(p.id)
        if not team_id:
            continue
        value = p.height_cm if require_height else _age_years(p.birth_date, today)
        index.setdefault(team_id, {}).setdefault(p.position, []).append({"id": p.id, "value": value, "name": p.known_as})

    return index


def _try_generate_slots(index: dict):
    team_ids = list(index.keys())
    for _ in range(200):
        random.shuffle(team_ids)
        used_teams = set()
        attempt = []
        ok = True
        for slot_id, role in enumerate(SLOT_ROLES):
            candidate = next((t for t in team_ids if t not in used_teams and index.get(t, {}).get(role)), None)
            if candidate is None:
                ok = False
                break
            used_teams.add(candidate)
            attempt.append({"slot_id": slot_id, "role": role, "team_id": candidate})
        if ok:
            return attempt
    return None


def generate_puzzle(db: Session) -> dict:
    criterion = random.choice(["youngest", "tallest"])
    index = _build_active_squad_index(db, criterion)
    slots = _try_generate_slots(index)

    if slots is None:
        # height_cm verisi henuz yeterince dolu degilse (backfill devam ediyor
        # olabilir) "tallest" cozulemeyebilir - "youngest"e dus.
        fallback = "youngest" if criterion == "tallest" else "tallest"
        criterion = fallback
        index = _build_active_squad_index(db, criterion)
        slots = _try_generate_slots(index)

    if slots is None:
        raise Exception("Extreme Squad bulmacası üretilemedi.")

    team_rows = db.query(models.Team).filter(models.Team.id.in_([s["team_id"] for s in slots])).all()
    team_name_map = {t.id: (t.short_name if t.short_name else t.name) for t in team_rows}

    theoretical_best = 0.0
    for s in slots:
        candidates = index[s["team_id"]][s["role"]]
        values = [c["value"] for c in candidates]
        theoretical_best += max(values) if criterion == "tallest" else min(values)

    return {
        "puzzle_id": str(uuid.uuid4()),
        "criterion": criterion,
        "slots": [{"slot_id": s["slot_id"], "role": s["role"], "team_id": s["team_id"], "team_name": team_name_map.get(s["team_id"], "?")} for s in slots],
        "theoretical_best": round(theoretical_best, 1),
    }


@router.get("/generate")
def generate(db: Session = Depends(get_db)):
    try:
        return generate_puzzle(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-single")
def validate_single(payload: dict, db: Session = Depends(get_db)):
    """payload = {"team_id": 123, "role": "Goalkeeper", "player_id": 456}"""
    team_id = payload.get("team_id")
    role = payload.get("role")
    player_id = payload.get("player_id")

    if not all([team_id, role, player_id]):
        raise HTTPException(status_code=400, detail="Eksik parametreler")

    player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not player:
        return {"valid": False, "message": "Oyuncu bulunamadı."}
    if not player.is_active:
        return {"valid": False, "message": f"{player.known_as} şu an aktif değil."}
    if player.position != role:
        return {"valid": False, "message": f"{player.known_as} bu mevkide oynamıyor."}

    latest_transfer = db.query(models.PlayerTransfer).filter(
        models.PlayerTransfer.player_id == player_id
    ).order_by(models.PlayerTransfer.transfer_date.desc()).first()

    if not latest_transfer or latest_transfer.to_team_id != team_id:
        team = db.query(models.Team).filter(models.Team.id == team_id).first()
        team_name = (team.short_name if team and team.short_name else team.name) if team else "bu takım"
        return {"valid": False, "message": f"{player.known_as}, {team_name} takımında aktif değil."}

    if not player.birth_date:
        return {"valid": False, "message": "Bu oyuncunun doğum tarihi kayıtlı değil."}

    return {"valid": True, "birth_date": player.birth_date, "height_cm": player.height_cm}


def compute_extreme_submission(db: Session, criterion: str, slots: list, player_ids: list) -> dict:
    """Saf hesaplama: verilen kadronun gecerliligini ve teorik en iyiye uzakligini hesaplar.

    Hem HTTP endpoint'i hem de multiplayer'daki online degerlendirme bu
    fonksiyonu paylasir. slots/player_ids ayni sirada (slot_id 0..10) eslenir.
    """
    index = _build_active_squad_index(db, criterion)

    used_teams = set()
    details = []
    valid_squad = len(player_ids) == len(slots)
    total_value = 0.0

    for i, slot in enumerate(slots):
        pid = player_ids[i] if i < len(player_ids) else None
        candidates = index.get(slot["team_id"], {}).get(slot["role"], [])
        cand_map = {c["id"]: c for c in candidates}

        ok = pid is not None and pid in cand_map and slot["team_id"] not in used_teams
        value = None
        name = None
        if ok:
            used_teams.add(slot["team_id"])
            value = cand_map[pid]["value"]
            name = cand_map[pid]["name"]
            total_value += value
        else:
            valid_squad = False

        details.append({"slot_id": slot["slot_id"], "player_id": pid, "name": name, "valid": ok, "value": value})

    theoretical_best = 0.0
    for s in slots:
        candidates = index.get(s["team_id"], {}).get(s["role"], [])
        if not candidates:
            continue
        values = [c["value"] for c in candidates]
        theoretical_best += max(values) if criterion == "tallest" else min(values)
    theoretical_best = round(theoretical_best, 1)

    if not valid_squad:
        return {
            "valid": False,
            "total_value": total_value,
            "theoretical_best": theoretical_best,
            "distance": 999999,
            "details": details,
            "xp_gained": 0,
            "tier": 4,
        }

    distance = abs(theoretical_best - total_value)
    deviation_percent = (distance / max(1.0, theoretical_best)) * 100

    xp_gained = 5
    tier = 4
    if distance == 0:
        xp_gained, tier = 25, 0
    elif deviation_percent <= 5.0:
        xp_gained, tier = 25, 1
    elif deviation_percent <= 15.0:
        xp_gained, tier = 15, 2
    elif deviation_percent <= 25.0:
        xp_gained, tier = 10, 3

    return {
        "valid": True,
        "total_value": total_value,
        "theoretical_best": theoretical_best,
        "distance": distance,
        "details": details,
        "xp_gained": xp_gained,
        "tier": tier,
    }


@router.post("/validate")
def validate(payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    criterion = payload.get("criterion")
    slots = payload.get("slots", [])
    player_ids = payload.get("player_ids", [])

    if criterion not in ("youngest", "tallest") or not slots:
        raise HTTPException(status_code=400, detail="Eksik parametreler")

    result = compute_extreme_submission(db, criterion, slots, player_ids)
    level_info = add_xp_and_check_level(db, current_user, result["xp_gained"])

    return {**result, **level_info}
