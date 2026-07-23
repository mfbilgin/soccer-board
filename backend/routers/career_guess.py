from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import random

import models
from database import get_db

router = APIRouter(prefix="/api/game/career-guess", tags=["Career Guess"])

@router.get("/generate")
def generate_career_guess(db: Session = Depends(get_db)):
    """
    Kariyer Geçmişi modunu üretir.
    En az 4 transferi (farklı takım geçmişi) olan, tercihen milli takımda
    20'den fazla cap yapmış popüler oyunculardan birini seçer.
    """
    valid_players_subquery = db.query(models.PlayerTransfer.player_id)\
        .group_by(models.PlayerTransfer.player_id)\
        .having(func.count(models.PlayerTransfer.id) >= 4)\
        .subquery()

    capped_players_subquery = db.query(models.PlayerNationalStat.player_id)\
        .group_by(models.PlayerNationalStat.player_id)\
        .having(func.sum(models.PlayerNationalStat.caps) > 20)\
        .subquery()

    random_player = db.query(models.Player).filter(
        models.Player.id.in_(db.query(valid_players_subquery.c.player_id)),
        models.Player.id.in_(db.query(capped_players_subquery.c.player_id))
    ).order_by(func.random()).first()

    if not random_player:
        random_player = db.query(models.Player).filter(
            models.Player.id.in_(db.query(valid_players_subquery.c.player_id))
        ).order_by(func.random()).first()

    if not random_player:
        raise HTTPException(status_code=500, detail="Yeterli takım geçmişine sahip oyuncu bulunamadı.")

    transfers = db.query(models.PlayerTransfer, models.Team)\
        .join(models.Team, models.PlayerTransfer.to_team_id == models.Team.id)\
        .filter(models.PlayerTransfer.player_id == random_player.id)\
        .order_by(models.PlayerTransfer.transfer_date.asc())\
        .all()

    teams_data = []
    for tr, t in transfers:
        teams_data.append({
            "team_id": t.id,
            "team_name": t.short_name or t.name,
            "logo_url": t.logo_url,
            "transfer_date": tr.transfer_date,
            "is_loan": "kiral" in (tr.transfer_fee or "").lower()
        })

    return {
        "target_player_id": random_player.id,
        "target_player_name": random_player.known_as,
        "career": teams_data
    }

@router.get("/verify")
def verify_career_guess(player_id: int, target_id: int):
    """
    Kullanıcının tahminini doğrular.
    """
    is_correct = (player_id == target_id)
    return {
        "correct": is_correct
    }
