from sqlalchemy.orm import Session
from models import User

RAKE_PERCENTAGE = 0.10

def deduct_entry_fee(db: Session, user_id: int, fee: int) -> bool:
    """Odaya giriş ücretini keser. Bakiye yetersizse False döner."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    if user.chips < fee:
        return False
        
    user.chips -= fee
    db.commit()
    db.refresh(user)
    return True

def award_winnings(db: Session, winner_id: int, total_pool: int) -> int:
    """Kazanan oyuncuya Rake (%10) kesildikten sonraki ödülü ekler."""
    user = db.query(User).filter(User.id == winner_id).first()
    if not user:
        return 0
    
    winnings = int(total_pool * (1 - RAKE_PERCENTAGE))
    user.chips += winnings
    db.commit()
    db.refresh(user)
    return winnings

def add_xp(db: Session, user_id: int, xp_amount: int):
    """Kullanıcıya XP ekler ve gerekiyorsa seviye (Level) atlatır."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return
        
    user.xp += xp_amount
    
    # GDD formula: XP = 100 * level^1.5 
    # => Level = (XP / 100) ^ (1/1.5)
    new_level = max(1, int((user.xp / 100) ** (1/1.5)))
    
    if new_level > user.level:
        user.level = new_level
        
    db.commit()
    db.refresh(user)
    return user.level

def update_rating(db: Session, winner_id: int, loser_id: int):
    """ELO (Rating) güncellemesini yapar."""
    winner = db.query(User).filter(User.id == winner_id).first()
    loser = db.query(User).filter(User.id == loser_id).first()
    
    if not winner or not loser:
        return
        
    # Basit Elo hesaplaması
    K = 32
    expected_winner = 1 / (1 + 10 ** ((loser.rating - winner.rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner.rating - loser.rating) / 400))
    
    winner.rating = int(winner.rating + K * (1 - expected_winner))
    loser.rating = int(loser.rating + K * (0 - expected_loser))
    
    db.commit()
    db.refresh(winner)
    db.refresh(loser)
    return winner.rating, loser.rating
