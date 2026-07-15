import sys
from database import SessionLocal
from models import Player, PlayerStats, PlayerTeamHistory, Team
from sqlalchemy import func

def verify(search_term):
    db = SessionLocal()
    player = db.query(Player).filter(Player.search_name.ilike(f"%{search_term.lower()}%")).first()
    if not player:
        print(f"HATA: '{search_term}' veritabanında bulunamadı veya henüz taranmadı!")
        return
        
    print(f"\n{'='*50}")
    print(f"OYUNCU: {player.known_as or player.full_name} (TM API ID: {player.api_id})")
    print(f"Milli Takım (Sadece Resmi): {player.international_caps} Maç | {player.international_goals} Gol | {player.international_assists} Asist | {player.international_yellow_cards} Sarı | {player.international_red_cards} Kırmızı")
    print(f"{'='*50}")
    
    # Turnuva İstatistikleri Toplamı
    print("\n--- TURNUVA BAZLI TOPLAM İSTATİSTİKLER ---")
    stats = db.query(
        PlayerStats.league_name,
        func.sum(PlayerStats.appearances).label('apps'),
        func.sum(PlayerStats.goals).label('goals'),
        func.sum(PlayerStats.assists).label('assists'),
        func.sum(PlayerStats.yellow_cards).label('yellow'),
        func.sum(PlayerStats.red_cards).label('red')
    ).filter(PlayerStats.player_id == player.id).group_by(PlayerStats.league_name).order_by(func.sum(PlayerStats.appearances).desc()).all()
    
    for s in stats:
        print(f"{s.league_name:<6} -> Maç: {s.apps:<3} | Gol: {s.goals:<3} | Asist: {s.assists:<3} | Sarı: {s.yellow:<3} | Kırmızı: {s.red}")
        
    # Kulüp Geçmişi
    print("\n--- KARİYERİ BOYUNCA OYNADIĞI KULÜPLER ---")
    history = db.query(Team).join(PlayerTeamHistory).filter(PlayerTeamHistory.player_id == player.id).all()
    for t in history:
        print(f"- {t.name}")
        
    print("\nNOT: Transfermarkt web sitesine girip 'Milli Takım' sekmesinden 'Hazırlık Maçları' filtrelemesi yaparak bu sayıları birebir teyit edebilirsiniz.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify(sys.argv[1])
    else:
        print("Kullanım: python verify_player.py 'oyuncu_adi'")
