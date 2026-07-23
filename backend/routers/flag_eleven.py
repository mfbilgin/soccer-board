from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from rapidfuzz import fuzz
from unidecode import unidecode
import random
import uuid
from collections import Counter

import models
from database import get_db

router = APIRouter(prefix="/api/game/flag-eleven", tags=["Flag Eleven"])

ROLE_SHORT = {"Goalkeeper": "GK", "Defender": "DEF", "Midfield": "MID", "Attack": "ATT"}

# puzzle_id -> {puzzle_id, positions, team_id, team_name, season, hint_country, hint_year, wrong_attempts}
# Yalnizca singleplayer HTTP generate/verify roundtrip icin - multiplayer kendi
# oda state'inde (room.game_state) tutar, bu cache'e hic dokunmaz.
PUZZLES = {}


def _is_match(guess: str, answer: str) -> bool:
    normalized_guess = unidecode(guess or "").lower().strip()
    normalized_answer = unidecode(answer or "").lower().strip()
    if not normalized_guess:
        return False
    return fuzz.WRatio(normalized_guess, normalized_answer) > 80


def _candidate_team_seasons(db: Session):
    rows = db.query(
        models.PlayerClubStat.team_id,
        models.PlayerClubStat.season,
        func.count(models.PlayerClubStat.player_id).label("cnt")
    ).filter(models.PlayerClubStat.appearances > 5).group_by(
        models.PlayerClubStat.team_id, models.PlayerClubStat.season
    ).having(func.count(models.PlayerClubStat.player_id) >= 11).all()
    return [(r.team_id, r.season) for r in rows]


def _top11(db: Session, team_id: int, season: str):
    rows = db.query(models.Player, models.PlayerClubStat.appearances).join(
        models.PlayerClubStat, models.PlayerClubStat.player_id == models.Player.id
    ).filter(
        models.PlayerClubStat.team_id == team_id,
        models.PlayerClubStat.season == season,
        models.Player.position.isnot(None),
        models.Player.position != "Missing",
        models.Player.nationality.isnot(None),
    ).order_by(models.PlayerClubStat.appearances.desc()).limit(11).all()
    return [p for p, _ in rows]


def generate_puzzle(db: Session) -> dict:
    """Tam ic temsil (cevap dahil) doner. HTTP katmani genel alanlari filtreler,
    multiplayer ise dogrudan room.game_state icinde saklar."""
    candidates = _candidate_team_seasons(db)
    if not candidates:
        raise Exception("Flag Eleven için uygun takım-sezon bulunamadı.")

    chosen = None
    top11 = None
    for _ in range(50):
        team_id, season = random.choice(candidates)
        players = _top11(db, team_id, season)
        if len(players) < 11:
            continue
        nat_counts = Counter(p.nationality for p in players)
        if max(nat_counts.values()) >= 6 and random.random() < (2 / 3):
            continue
        chosen = (team_id, season)
        top11 = players
        break

    if not chosen:
        raise Exception("Flag Eleven bulmacası üretilemedi.")

    team_id, season = chosen
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    team_name = (team.short_name if team and team.short_name else team.name) if team else "?"

    role_counters = {}
    positions = []
    for p in top11:
        role = p.position
        role_counters[role] = role_counters.get(role, 0) + 1
        slot = f"{ROLE_SHORT.get(role, 'SUB')}{role_counters[role]}"
        positions.append({"slot": slot, "nationality": p.nationality})

    year = season.split("-")[0] if season else "?"

    return {
        "puzzle_id": str(uuid.uuid4()),
        "positions": positions,
        "team_id": team_id,
        "team_name": team_name,
        "season": season,
        "hint_country": team.country if team else None,
        "hint_year": year,
    }


@router.get("/generate")
def generate(db: Session = Depends(get_db)):
    try:
        puzzle = generate_puzzle(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    PUZZLES[puzzle["puzzle_id"]] = {**puzzle, "wrong_attempts": 0}
    return {"puzzle_id": puzzle["puzzle_id"], "positions": puzzle["positions"]}


@router.post("/verify")
def verify(payload: dict):
    puzzle_id = payload.get("puzzle_id")
    team_guess = payload.get("team_guess", "")

    puzzle = PUZZLES.get(puzzle_id)
    if not puzzle:
        raise HTTPException(status_code=404, detail="Bulmaca bulunamadı veya süresi doldu.")

    if _is_match(team_guess, puzzle["team_name"]):
        del PUZZLES[puzzle_id]
        return {"correct": True, "team_name": puzzle["team_name"]}

    puzzle["wrong_attempts"] += 1
    hints = {}
    if puzzle["wrong_attempts"] >= 1:
        hints["country"] = puzzle["hint_country"]
    if puzzle["wrong_attempts"] >= 2:
        hints["year"] = puzzle["hint_year"]

    response = {"correct": False, "hints": hints, "wrong_attempts": puzzle["wrong_attempts"]}
    if puzzle["wrong_attempts"] >= 3:
        response["team_name"] = puzzle["team_name"]
        del PUZZLES[puzzle_id]

    return response
