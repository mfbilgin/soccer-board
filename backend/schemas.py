from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class TeamResponse(BaseModel):
    api_id: str
    name: str

class PlayerResponse(BaseModel):
    id: int
    api_id: str
    known_as: str
    nationality: Optional[str] = None
    birth_date: Optional[date] = None
    height_cm: Optional[float] = None
    position: Optional[str] = None
    image_url: Optional[str] = None

class SearchResultItem(BaseModel):
    id: int
    name: str
    type: int # 1 = Player, 2 = Team
    subtitle: Optional[str] = None

class SearchResponse(BaseModel):
    results: List[SearchResultItem]
    
    class Config:
        from_attributes = True

# --- AUTH & USER SCHEMAS ---

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    xp: int
    level: int
    chips: int
    gems: int
    rating: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- SOCIAL SCHEMAS ---
class FriendRequest(BaseModel):
    username: str

class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    rating: int
    level: int
    
class LeaderboardResponse(BaseModel):
    entries: List[LeaderboardEntry]

# --- GAME SCHEMAS ---

class CellItem(BaseModel):
    id: int
    name: str

class GridResponse(BaseModel):
    grid_id: str
    type: int # 1 = Team x Team, 2 = Player x Player
    rows: List[CellItem]
    cols: List[CellItem]

class GuessRequest(BaseModel):
    grid_id: str
    row_id: int # Team ID veya Player ID
    col_id: int # Team ID veya Player ID
    guess_id: int # Kullanıcının tahmin ettiği Player ID veya Team ID
    type: int # Matris türü

class GuessResponse(BaseModel):
    correct: bool
    message: str
    # Eğer doğruysa tahmin edilen kişinin/takımın detayları dönebilir
    matched_name: Optional[str] = None


