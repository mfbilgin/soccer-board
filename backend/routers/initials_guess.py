import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from initials_guess import InitialsGuessEngine

router = APIRouter(prefix="/api/game/initials-guess", tags=["Initials Guess"])


@router.get("/letter-pools")
def letter_pools(db: Session = Depends(get_db)):
    try:
        engine = InitialsGuessEngine(db)
        pools = engine.generate_letter_pools()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    start_letter = random.choice(pools["start_pool"])
    end_letter = random.choice(pools["end_pool"])
    return {**pools, "start_letter": start_letter, "end_letter": end_letter}


@router.post("/verify")
def verify(payload: dict, db: Session = Depends(get_db)):
    start_letter = payload.get("start_letter")
    end_letter = payload.get("end_letter")
    player_id = payload.get("player_id")

    if not all([start_letter, end_letter, player_id]):
        raise HTTPException(status_code=400, detail="Eksik parametreler")

    engine = InitialsGuessEngine(db)
    correct = engine.validate_guess(start_letter, end_letter, player_id)
    return {"correct": correct}


@router.get("/reveal")
def reveal(start_letter: str, end_letter: str, db: Session = Depends(get_db)):
    engine = InitialsGuessEngine(db)
    answer = engine.get_example_answer(start_letter, end_letter)
    if not answer:
        raise HTTPException(status_code=404, detail="Örnek cevap bulunamadı.")
    return {"answer": answer}
