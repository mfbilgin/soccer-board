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
    En az 4 transferi (farklı takım geçmişi) olan popüler oyunculardan birini seçer.
    """
    valid_players_subquery = db.query(models.PlayerTeamHistory.player_id)\
        .group_by(models.PlayerTeamHistory.player_id)\
        .having(func.count(models.PlayerTeamHistory.id) >= 4)\
        .subquery()
        
    random_player = db.query(models.Player).filter(
        models.Player.id.in_(valid_players_subquery),
        models.Player.international_caps > 20
    ).order_by(func.random()).first()
    
    if not random_player:
        random_player = db.query(models.Player).filter(
            models.Player.id.in_(valid_players_subquery)
        ).order_by(func.random()).first()
        
    if not random_player:
        raise HTTPException(status_code=500, detail="Yeterli takım geçmişine sahip oyuncu bulunamadı.")
        
    history = db.query(models.PlayerTeamHistory, models.Team)\
        .join(models.Team, models.PlayerTeamHistory.team_id == models.Team.id)\
        .filter(models.PlayerTeamHistory.player_id == random_player.id)\
        .order_by(models.PlayerTeamHistory.start_year.asc())\
        .all()
        
    teams_data = []
    for h, t in history:
        teams_data.append({
            "team_id": t.id,
            "team_name": t.known_as or t.name,
            "logo_url": t.logo_url,
            "start_year": h.start_year,
            "end_year": h.end_year
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
