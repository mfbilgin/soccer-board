from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import random
import uuid
import math

import models
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/mode31", tags=["Mode 3.1: Kariyer İstatistiği Avı"])

CLUB_METRICS = ["goals", "assists", "appearances", "yellow_cards", "minutes_played"]
INT_METRICS = ["goals", "assists", "caps"]

POPULAR_LEAGUES = {
    "GB1": "Premier League (İngiltere)",
    "ES1": "La Liga (İspanya)",
    "IT1": "Serie A (İtalya)",
    "L1": "Bundesliga (Almanya)",
    "FR1": "Ligue 1 (Fransa)",
    "TR1": "Trendyol Süper Lig",
    "INT": "Milli Maçlar"
}

def round_target(val: int, metric: str) -> int:
    if val == 0:
        return 0
    if metric == "minutes_played":
        # round to nearest 100
        return max(100, int(math.ceil(val / 100.0)) * 100)
    else:
        # round to nearest 10
        return max(10, int(math.ceil(val / 10.0)) * 10)

@router.get("/generate")
def generate_puzzle(db: Session = Depends(get_db)):
    league_code = random.choice(list(POPULAR_LEAGUES.keys()))
    league_name = POPULAR_LEAGUES[league_code]
    
    player_count = random.choice([3, 5])
    
    if league_code == "INT":
        metric = random.choice(INT_METRICS)
        metric_column = getattr(models.PlayerNationalStats, metric)
        
        # Group by player to get total national stats (in case of multiple rows, though national might be aggregated)
        top_players_query = db.query(
            models.PlayerNationalStats.player_id,
            func.sum(metric_column).label("total_stat")
        ).group_by(models.PlayerNationalStats.player_id) \
         .having(func.sum(metric_column) > 0) \
         .order_by(func.random()) \
         .limit(50).all()
         
    else:
        metric = random.choice(CLUB_METRICS)
        metric_column = getattr(models.PlayerClubStats, metric)
        
        comp = db.query(models.Competition).filter(models.Competition.name == league_code).first()
        if not comp:
            raise HTTPException(status_code=500, detail="League not found in DB")
            
        top_players_query = db.query(
            models.PlayerClubStats.player_id,
            func.sum(metric_column).label("total_stat")
        ).filter(models.PlayerClubStats.competition_id == comp.id) \
         .group_by(models.PlayerClubStats.player_id) \
         .having(func.sum(metric_column) > 0) \
         .order_by(func.random()) \
         .limit(50).all()

    valid_players = [{"id": p[0], "stat": p[1]} for p in top_players_query]
    
    if len(valid_players) < player_count:
        target_value = random.randint(50, 300)
        target_value = round_target(target_value, metric)
    else:
        chosen = random.sample(valid_players, player_count)
        raw_sum = sum(p["stat"] for p in chosen)
        target_value = round_target(raw_sum, metric)
        
    puzzle_id = str(uuid.uuid4())
    
    return {
        "puzzle_id": puzzle_id,
        "league": league_code,
        "league_name": league_name,
        "metric": metric,
        "player_count": player_count,
        "target": target_value
    }

@router.post("/validate-single")
def validate_single(payload: dict, db: Session = Depends(get_db)):
    """
    Dummy Engeli: Oyuncunun o ligde belirtilen metrik için >0 değeri olup olmadığını kontrol eder.
    payload = {"league": "GB1", "metric": "goals", "player_id": 123}
    """
    league = payload.get("league")
    metric = payload.get("metric")
    player_id = payload.get("player_id")
    
    if not all([league, metric, player_id]):
        raise HTTPException(status_code=400, detail="Missing parameters")
        
    if league == "INT":
        if metric not in INT_METRICS:
            return {"valid": False, "message": f"Milli takım için {metric} geçersiz."}
        
        caps_total = db.query(func.sum(models.PlayerNationalStats.caps)).filter(
            models.PlayerNationalStats.player_id == player_id
        ).scalar() or 0
        
        if caps_total > 0:
            col = getattr(models.PlayerNationalStats, metric)
            total = db.query(func.sum(col)).filter(models.PlayerNationalStats.player_id == player_id).scalar() or 0
            return {"valid": True, "value": total}
        else:
            return {"valid": False, "message": "Bu oyuncu milli takımda oynamamış."}

    else:
        if metric not in CLUB_METRICS:
            return {"valid": False, "message": f"Kulüp için {metric} geçersiz."}
        comp = db.query(models.Competition).filter(models.Competition.name == league).first()
        if not comp:
            return {"valid": False, "message": "Lig bulunamadı."}
            
        apps_total = db.query(func.sum(models.PlayerClubStats.appearances)).filter(
            models.PlayerClubStats.player_id == player_id,
            models.PlayerClubStats.competition_id == comp.id
        ).scalar() or 0
        
        if apps_total > 0:
            col = getattr(models.PlayerClubStats, metric)
            total = db.query(func.sum(col)).filter(
                models.PlayerClubStats.player_id == player_id,
                models.PlayerClubStats.competition_id == comp.id
            ).scalar() or 0
            return {"valid": True, "value": total}
        else:
            return {"valid": False, "message": "Bu oyuncu bu ligde oynamamış."}

@router.post("/validate")
def validate_submission(payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    league = payload.get("league")
    metric = payload.get("metric")
    player_ids = payload.get("player_ids", [])
    target = payload.get("target")
    
    if not all([league, metric, player_ids, target is None]): # target 0 olabilir, bu yüzden is None kontrolü
        if target is None:
            raise HTTPException(status_code=400, detail="Eksik parametreler")
            
    total_sum = 0
    results = []
    
    for pid in player_ids:
        # validate-single mantığıyla çek
        if league == "INT":
            col = getattr(models.PlayerNationalStats, metric)
            val = db.query(func.sum(col)).filter(models.PlayerNationalStats.player_id == pid).scalar()
        else:
            comp = db.query(models.Competition).filter(models.Competition.name == league).first()
            col = getattr(models.PlayerClubStats, metric)
            val = db.query(func.sum(col)).filter(
                models.PlayerClubStats.player_id == pid,
                models.PlayerClubStats.competition_id == comp.id if comp else -1
            ).scalar()
            
        val = val or 0
        total_sum += val
        
        player = db.query(models.Player).filter(models.Player.id == pid).first()
        name = player.known_as if player else "Bilinmeyen"
        results.append({
            "player_id": pid,
            "name": name,
            "value": val
        })
        
    distance = abs(target - total_sum)
    
    # Yeni XP Mantığı (%1 ve %10 kuralı)
    # distance 0 ise %0 sapma.
    # %1 sapma hesaplaması
    deviation_percent = (distance / max(1, target)) * 100
    
    xp_gained = 5
    if deviation_percent <= 1.0:
        xp_gained = 25
    elif deviation_percent <= 10.0:
        xp_gained = 10
        
    current_user.xp += xp_gained
    leveled_up = False
    required_xp = int(100 * (current_user.level ** 1.5))
    
    while current_user.xp >= required_xp:
        current_user.xp -= required_xp
        current_user.level += 1
        leveled_up = True
        required_xp = int(100 * (current_user.level ** 1.5))
        
    db.commit()
    db.refresh(current_user)
        
    return {
        "total_sum": total_sum,
        "target": target,
        "distance": distance,
        "details": results,
        "xp_gained": xp_gained,
        "new_xp": current_user.xp,
        "new_level": current_user.level,
        "required_xp": required_xp,
        "leveled_up": leveled_up
    }
