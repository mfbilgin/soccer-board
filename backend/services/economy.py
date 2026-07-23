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

def add_xp_and_check_level(db: Session, user: User, xp_amount: int) -> dict:
    """Kullanıcıya XP ekler, seviye barını doldukça sıfırlayarak level atlatır.

    Kanonik formül (target_score.py'den taşındı): required_xp = 100 * level^1.5,
    xp bu eşiği geçtikçe düşülür ve level artar (tek seferde birden fazla
    seviye atlanabilir).
    """
    user.xp += xp_amount
    leveled_up = False
    required_xp = int(100 * (user.level ** 1.5))

    while user.xp >= required_xp:
        user.xp -= required_xp
        user.level += 1
        leveled_up = True
        required_xp = int(100 * (user.level ** 1.5))

    db.commit()
    db.refresh(user)

    return {
        "new_xp": user.xp,
        "new_level": user.level,
        "required_xp": required_xp,
        "leveled_up": leveled_up,
    }

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
