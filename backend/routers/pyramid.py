from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import random

import models
from database import get_db

router = APIRouter(prefix="/api/game/pyramid", tags=["Pyramid"])

LEAGUES = {
    'GB1': 'Premier League',
    'ES1': 'La Liga',
    'IT1': 'Serie A',
    'FR1': 'Ligue 1',
    'L1': 'Bundesliga',
    'TR1': 'Süper Lig'
}

STATS = ['goals', 'assists', 'appearances']

TEAMS = [
    'Real Madrid', 'Barcelona', 'Atlético de Madrid', 'Bayern Munich', 'Arsenal', 
    'Paris Saint-Germain', 'Inter', 'Manchester City', 'Liverpool', 'Chelsea', 
    'Manchester United', 'Milan', 'Fenerbahçe', 'Juventus', 'Galatasaray', 'Beşiktaş'
]

def generate_puzzle(db: Session) -> dict:
    """Ic temsil - gizlenmesi gereken hucreler dahil TUM isimleri icerir.
    Singleplayer endpoint'i (mevcut davranisi korumak icin) oldugu gibi
    dondurur; multiplayer ise yayinlamadan once gizli hucrelerin ismini
    kirpar (bkz. routers/multiplayer.py._top10_public_items)."""
    # Rastgele bir tür seç: 0 = Kulüp Ligi (Gol/Asist/Maç), 1 = Milli Takım (Gol), 2 = Takım Bazlı (Kariyer Toplamı)
    mode = random.choice([0, 1, 2])
    
    items = []
    if mode == 1:
        # Milli Takım Modu
        top_players = db.query(
            models.Player.id,
            models.Player.known_as,
            func.sum(models.PlayerNationalStat.goals).label('total_stat')
        ).join(
            models.PlayerNationalStat, models.PlayerNationalStat.player_id == models.Player.id
        ).group_by(models.Player.id).having(func.sum(models.PlayerNationalStat.goals) > 0).order_by(func.sum(models.PlayerNationalStat.goals).desc()).limit(10).all()
        
        title = "Milli Takım"
        subtitle = "En Çok Gol Atanlar"
        
        if len(top_players) < 10:
            raise HTTPException(status_code=500, detail="Yeterli veri bulunamadı.")
            
        for idx, p in enumerate(top_players):
            is_hidden = idx >= 3
            items.append({
                "rank": idx + 1,
                "id": p.id,
                "name": p.known_as,
                "score": p.total_stat,
                "hidden": is_hidden
            })
    elif mode == 0:
        # Kulüp Ligi Modu
        league_code = random.choice(list(LEAGUES.keys()))
        league_name = LEAGUES[league_code]
        stat_type = random.choice(STATS)
        
        stat_col = getattr(models.PlayerClubStat, stat_type)
        
        comp = db.query(models.Competition).filter(models.Competition.name == league_code).first()
        if not comp:
             raise HTTPException(status_code=500, detail="Lig bulunamadı.")
             
        # İlgili ligde en çok gol/asist yapan ilk 10 oyuncuyu bul
        top_players = db.query(
            models.Player.id, 
            models.Player.known_as, 
            func.sum(stat_col).label('total_stat')
        ).join(
            models.PlayerClubStat, models.PlayerClubStat.player_id == models.Player.id
        ).filter(
            models.PlayerClubStat.competition_id == comp.id
        ).group_by(models.Player.id).having(func.sum(stat_col) > 0).order_by(func.sum(stat_col).desc()).limit(10).all()
        
        if len(top_players) < 10:
            raise HTTPException(status_code=500, detail="Yeterli veri bulunamadı.")
            
        title = league_name
        if stat_type == 'goals':
            subtitle = "En Çok Gol Atanlar"
        elif stat_type == 'assists':
            subtitle = "En Çok Asist Yapanlar"
        else:
            subtitle = "En Çok Maça Çıkanlar"
        
        for idx, p in enumerate(top_players):
            is_hidden = idx >= 3
            items.append({
                "rank": idx + 1,
                "id": p.id,
                "name": p.known_as,
                "score": p.total_stat,
                "hidden": is_hidden
            })
    elif mode == 2:
        # Takım Bazlı Mod
        team_name = random.choice(TEAMS)
        stat_type = random.choice(STATS)
        
        stat_col = getattr(models.PlayerClubStat, stat_type)
            
        title = team_name
        if stat_type == 'goals':
            subtitle = "Formayla En Çok Gol Atanlar"
        elif stat_type == 'assists':
            subtitle = "Formayla En Çok Asist Yapanlar"
        else:
            subtitle = "Formayla En Çok Maça Çıkanlar"
            
        team = db.query(models.Team).filter(
            (models.Team.name.ilike(f"%{team_name}%")) | (models.Team.short_name.ilike(f"%{team_name}%"))
        ).order_by(func.length(models.Team.name)).first()
        
        if not team:
             raise HTTPException(status_code=500, detail=f"Takım bulunamadı: {team_name}")
             
        top_players = db.query(
            models.Player.id,
            models.Player.known_as,
            func.sum(stat_col).label('total_stat')
        ).join(
            models.PlayerClubStat, models.PlayerClubStat.player_id == models.Player.id
        ).filter(
            models.PlayerClubStat.team_id == team.id
        ).group_by(
            models.Player.id
        ).having(
            func.sum(stat_col) > 0
        ).order_by(
            func.sum(stat_col).desc()
        ).limit(10).all()

        if len(top_players) < 10:
            raise HTTPException(status_code=500, detail="Yeterli veri bulunamadı.")
            
        for idx, p in enumerate(top_players):
            is_hidden = idx >= 3
            items.append({
                "rank": idx + 1,
                "id": p.id,
                "name": p.known_as,
                "score": p.total_stat,
                "hidden": is_hidden
            })
        
    return {
        "title": title,
        "subtitle": subtitle,
        "items": items
    }

@router.get("/generate")
def generate_pyramid(db: Session = Depends(get_db)):
    return generate_puzzle(db)
