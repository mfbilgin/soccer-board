from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

import models, schemas
from database import get_db
from routers.auth import get_current_user

router = APIRouter(prefix="/api/social", tags=["Social"])

@router.get("/leaderboard/global", response_model=schemas.LeaderboardResponse)
def get_global_leaderboard(db: Session = Depends(get_db)):
    top_users = db.query(models.User).order_by(models.User.rating.desc()).limit(50).all()
    entries = []
    for idx, user in enumerate(top_users):
        entries.append(schemas.LeaderboardEntry(
            rank=idx + 1,
            username=user.username,
            rating=user.rating,
            level=user.level
        ))
    return {"entries": entries}

@router.post("/friends/add")
def add_friend(request: schemas.FriendRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    target_user = db.query(models.User).filter(models.User.username == request.username).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot add yourself as friend")
        
    existing = db.query(models.Friendship).filter(
        or_(
            and_(models.Friendship.user_id == current_user.id, models.Friendship.friend_id == target_user.id),
            and_(models.Friendship.user_id == target_user.id, models.Friendship.friend_id == current_user.id)
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Friendship or request already exists")
        
    new_friendship = models.Friendship(user_id=current_user.id, friend_id=target_user.id, status="pending")
    db.add(new_friendship)
    db.commit()
    return {"message": "Friend request sent"}

@router.get("/friends")
def get_friends(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Friends where status="accepted"
    friendships = db.query(models.Friendship).filter(
        and_(
            or_(models.Friendship.user_id == current_user.id, models.Friendship.friend_id == current_user.id),
            models.Friendship.status == "accepted"
        )
    ).all()
    
    friends_list = []
    for f in friendships:
        if f.user_id == current_user.id:
            friend_user = db.query(models.User).filter(models.User.id == f.friend_id).first()
        else:
            friend_user = db.query(models.User).filter(models.User.id == f.user_id).first()
            
        friends_list.append({
            "username": friend_user.username,
            "level": friend_user.level,
            "rating": friend_user.rating
        })
        
    # Sıralamayı ELO'ya göre yap (Arkadaş lider tablosu için)
    friends_list.sort(key=lambda x: x["rating"], reverse=True)
    return {"friends": friends_list}
