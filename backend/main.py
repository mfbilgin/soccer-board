# Football Trivia API Main Entry Point

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_

import models
import schemas
from database import get_db, engine
from routers import auth, game, pyramid, social, multiplayer, mode_3_1, career_guess

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Football Trivia API", version="1.0.0")

# Router'ları (API Gruplarını) Kaydet
app.include_router(auth.router)
app.include_router(game.router)
app.include_router(pyramid.router)
app.include_router(social.router)
app.include_router(multiplayer.router)
app.include_router(multiplayer.ws_router)
app.include_router(mode_3_1.router)
app.include_router(career_guess.router)

# Güvenlik ve CORS Ayarları
# Production ortamında allow_origins spesifik domainlerle kısıtlanmalıdır.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Geliştirme aşaması için tüm portlara açık
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Football Trivia API is running. Ready for kick-off!"}

@app.get("/api/players/search", response_model=schemas.SearchResponse)
def search_players(
    name: str = Query(..., min_length=3, description="Aranacak oyuncu adı (en az 3 harf)"),
    db: Session = Depends(get_db)
):
    """
    Fuzzy Search (Benzerlik) mantığıyla çalışan güvenli arama endpointi.
    SQLite için iLIKE benzeri sorgu kullanır. SQL Injection'a karşı Pydantic ve SQLAlchemy ile %100 güvenlidir.
    """
    # % işareti ile kelimenin içinde geçenleri buluyoruz
    search_term = f"%{name}%"
    
    # known_as sütununda büyük/küçük harf duyarsız arama
    players = db.query(models.Player)\
                .filter(models.Player.known_as.ilike(search_term))\
                .limit(10)\
                .all()
    
    if not players:
        return {"players": []}
        
    return {"players": players}
