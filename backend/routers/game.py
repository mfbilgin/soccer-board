from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import case, func
import random

import schemas
from database import get_db
from routers.auth import get_current_user
from tictactoe import TicTacToeEngine
from rapidfuzz import process, fuzz
from services.economy import add_xp_and_check_level

# --- FUZZY SEARCH CACHE ---
PLAYER_CACHE = []
PLAYER_CHOICES = []

TEAM_CACHE = []
TEAM_CHOICES = []

CACHE_LOADED = False

def ensure_cache(db: Session):
    global PLAYER_CACHE, PLAYER_CHOICES, TEAM_CACHE, TEAM_CHOICES, CACHE_LOADED
    if CACHE_LOADED:
        return
    import models
    # Oyuncuları cache'e al (Milli maç sayılarıyla birlikte)
    players = db.query(
        models.Player.id, 
        models.Player.known_as, 
        models.Player.search_name, 
        models.Player.birth_date, 
        models.Player.nationality, 
        models.Player.position,
        func.coalesce(func.sum(models.PlayerNationalStat.caps), 0).label('total_caps')
    ).outerjoin(models.PlayerNationalStat).group_by(models.Player.id).all()
    
    for p in players:
        PLAYER_CACHE.append({
            "id": p.id,
            "name": p.known_as,
            "birth_date": p.birth_date,
            "nationality": p.nationality,
            "position": p.position,
            "caps": p.total_caps
        })
        PLAYER_CHOICES.append(p.search_name)
        
    # Takımları cache'e al (Sadece en az 1 oyuncusu olan takımlar)
    valid_team_ids = db.query(models.PlayerClubStat.team_id).distinct()
    teams = db.query(models.Team.id, models.Team.name, models.Team.short_name, models.Team.country)\
              .filter(models.Team.id.in_(valid_team_ids)).all()
    for t in teams:
        TEAM_CACHE.append({
            "id": t.id,
            "name": t.short_name if t.short_name else t.name,
            "country": t.country
        })
        TEAM_CHOICES.append(t.short_name if t.short_name else t.name)
        
    CACHE_LOADED = True
# --------------------------

router = APIRouter(prefix="/api/game/tictactoe", tags=["Tic-Tac-Toe"])

@router.get("/grid", response_model=schemas.GridResponse)
def get_grid(
    type: int = Query(None, description="1 for TeamxTeam, 2 for PlayerxPlayer. Random if not provided."),
    db: Session = Depends(get_db)
):
    engine = TicTacToeEngine(db)
    
    if type is None:
        type = random.choice([1, 2])
        
    try:
        if type == 1:
            grid = engine.generate_type1_grid()
        elif type == 2:
            grid = engine.generate_type2_grid()
        else:
            raise HTTPException(status_code=400, detail="Invalid grid type. Must be 1 or 2.")
            
        return grid
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guess", response_model=schemas.GuessResponse)
def make_guess(guess: schemas.GuessRequest, db: Session = Depends(get_db)):
    engine = TicTacToeEngine(db)
    is_correct, message, matched_name = engine.validate_guess(
        row_id=guess.row_id,
        col_id=guess.col_id,
        guess_id=guess.guess_id,
        grid_type=guess.type
    )
    
    return {
        "correct": is_correct,
        "message": message,
        "matched_name": matched_name
    }

from pydantic import BaseModel
from typing import List

class SurrenderRequest(BaseModel):
    grid_type: int
    row_ids: List[int]
    col_ids: List[int]
    correct_count: int = 0

@router.post("/surrender")
def surrender_game(req: SurrenderRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    engine = TicTacToeEngine(db)
    answers = engine.get_answers(req.grid_type, req.row_ids, req.col_ids)

    xp_gained = req.correct_count * 10
    level_info = {}
    if xp_gained > 0 and current_user:
        level_info = add_xp_and_check_level(db, current_user, xp_gained)

    return {"answers": answers, "xp_gained": xp_gained, **level_info}

@router.get("/search", response_model=schemas.SearchResponse)
def search_entity(
    q: str = Query(..., min_length=2, description="Arama metni"),
    type: int = Query(..., description="Aranacak tip: 1=Oyuncu (Grid 1 için), 2=Takım (Grid 2 için)"),
    db: Session = Depends(get_db)
):
    import models
    from unidecode import unidecode
    results = []
    
    # Kullanıcının aramasını aksansız ve küçük harfe çevir
    normalized_q = unidecode(q).lower()
    
    # Fuzzy cache'in yüklendiğinden emin ol
    ensure_cache(db)
    
    if type == 1:
        # Oyuncu Ara - Önceliklendirme: Popülerlik (Milli Maç) > Tam eşleşme > Başlayan > Kelime Başı > İçinde geçen ve isim kısalığı
        players = db.query(
            models.Player,
            func.coalesce(func.sum(models.PlayerNationalStat.caps), 0).label('total_caps')
        ).outerjoin(models.PlayerNationalStat).filter(
            models.Player.search_name.ilike(f"%{normalized_q}%") | models.Player.known_as.ilike(f"%{q}%")
        ).group_by(models.Player.id).order_by(
            models.Player.is_active.desc(),
            func.coalesce(func.sum(models.PlayerNationalStat.caps), 0).desc(),
            case(
                (models.Player.known_as.ilike(q), 1),
                (models.Player.search_name.ilike(normalized_q), 1),
                (models.Player.known_as.ilike(f"{q}%"), 2),
                (models.Player.search_name.ilike(f"{normalized_q}%"), 2),
                (models.Player.known_as.ilike(f"% {q}%"), 3),
                (models.Player.search_name.ilike(f"% {normalized_q}%"), 3),
                else_=4
            ),
            func.length(models.Player.known_as)
        ).limit(10).all()
        found_ids = set()
        for p, caps in players:
            found_ids.add(p.id)
            year = p.birth_date.split("-")[0] if p.birth_date else ""
            nat = p.nationality if p.nationality else ""
            pos = p.position if p.position else ""
            sub_parts = [s for s in [nat, year, pos] if s]
            subtitle = " - ".join(sub_parts) if sub_parts else None
            results.append({
                "id": p.id,
                "name": p.known_as,
                "type": 1,
                "subtitle": subtitle
            })
            
        # Eğer yeterli SQL sonucu yoksa, rapidfuzz ile eksikleri tamamla
        if len(results) < 10:
            fuzzy_matches = process.extract(normalized_q, PLAYER_CHOICES, scorer=fuzz.WRatio, limit=20)
            
            # Fuzzy matchleri caps sayısına göre sırala (popülerlik)
            sorted_fuzzy = sorted(fuzzy_matches, key=lambda x: PLAYER_CACHE[x[2]]["caps"], reverse=True)
            
            for match_str, score, idx in sorted_fuzzy:
                if len(results) >= 10:
                    break
                # Skor %60'ın üzerindeyse ve harf hatası makulse kabul et
                if score > 60:
                    p = PLAYER_CACHE[idx]
                    if p["id"] not in found_ids:
                        found_ids.add(p["id"])
                        year = p["birth_date"].split("-")[0] if p["birth_date"] else ""
                        nat = p["nationality"] if p["nationality"] else ""
                        pos = p["position"] if p["position"] else ""
                        sub_parts = [s for s in [nat, year, pos] if s]
                        subtitle = " - ".join(sub_parts) if sub_parts else None
                        results.append({
                            "id": p["id"],
                            "name": p["name"],
                            "type": 1,
                            "subtitle": subtitle
                        })
                        
    elif type == 2:
        # Takım Ara - Önceliklendirme: Tam eşleşme > Başlayan > Kelime Başı > İçinde geçen ve isim kısalığı
        teams = db.query(models.Team).filter(
            models.Team.name.ilike(f"%{q}%") | models.Team.short_name.ilike(f"%{q}%")
        ).order_by(
            case(
                (models.Team.short_name.ilike(q), 1),
                (models.Team.name.ilike(q), 1),
                (models.Team.short_name.ilike(f"{q}%"), 2),
                (models.Team.name.ilike(f"{q}%"), 2),
                (models.Team.short_name.ilike(f"% {q}%"), 3),
                (models.Team.name.ilike(f"% {q}%"), 3),
                else_=4
            ),
            func.length(models.Team.name)
        ).limit(10).all()
        found_ids = set()
        for t in teams:
            found_ids.add(t.id)
            results.append({
                "id": t.id,
                "name": t.short_name if t.short_name else t.name,
                "type": 2,
                "subtitle": t.country if t.country else None
            })
            
        # Eğer yeterli SQL sonucu yoksa, rapidfuzz ile eksikleri tamamla
        if len(results) < 10:
            fuzzy_matches = process.extract(normalized_q, TEAM_CHOICES, scorer=fuzz.WRatio, limit=20)
            for match_str, score, idx in fuzzy_matches:
                if len(results) >= 10:
                    break
                if score > 60:
                    t = TEAM_CACHE[idx]
                    if t["id"] not in found_ids:
                        found_ids.add(t["id"])
                        results.append({
                            "id": t["id"],
                            "name": t["name"],
                            "type": 2,
                            "subtitle": t["country"] if t["country"] else None
                        })
    else:
        raise HTTPException(status_code=400, detail="Geçersiz arama tipi")

    return {"results": results}
