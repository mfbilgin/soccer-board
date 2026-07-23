import os
import sys

# Eğer Windows'ta test edecekseniz konsola export yerine şunu yazın:
# $env:DATABASE_URL_V2="postgresql://..."

# Modülleri içe aktaralım
try:
    from database_v2 import SessionLocalV2, engine
    from models_v2 import Player, Team, Competition, PlayerClubStat, PlayerTransfer, PlayerHonour
except ImportError as e:
    print(f"Modüller yüklenirken hata oluştu: {e}")
    sys.exit(1)

def verify_data():
    db = SessionLocalV2()
    
    print("====== KUSURSUZ ŞEMA (V2) VERİ DOĞRULAMA ======\n")
    
    # 1. Toplam Veri Sayıları
    player_count = db.query(Player).count()
    team_count = db.query(Team).count()
    comp_count = db.query(Competition).count()
    stat_count = db.query(PlayerClubStat).count()
    trans_count = db.query(PlayerTransfer).count()
    honour_count = db.query(PlayerHonour).count()
    
    print(f"Toplam Kayıtlı Oyuncu: {player_count}")
    print(f"Toplam Kayıtlı Takım: {team_count}")
    print(f"Toplam Kayıtlı Turnuva/Lig: {comp_count}")
    print(f"Toplam Kulüp İstatistiği Satırı: {stat_count}")
    print(f"Toplam Transfer Geçmişi: {trans_count}")
    print(f"Toplam Kazanılan Kupa: {honour_count}")
    print("-" * 50)
    
    if player_count == 0:
        print("Veritabanı henüz boş. Scraper'ın biraz daha çalışmasına izin verin.")
        return
        
    # 2. Rastgele veya en dolu oyunculardan birini seçelim
    # Rastgele bir oyuncu (verisi en dolu olanlardan)
    test_player = db.query(Player).filter(Player.name != None).order_by(Player.id.desc()).first()
    
    if not test_player:
        print("Henüz profili tam çekilmiş bir oyuncu yok.")
        return
        
    print(f"ÖRNEK OYUNCU TESTİ: {test_player.known_as or test_player.name}")
    print(f"Uyruk: {test_player.nationality} | Pozisyon: {test_player.position}")
    print("-" * 50)
    
    # İstatistikler
    stats = db.query(PlayerClubStat).filter_by(player_id=test_player.id).limit(5).all()
    print("Oynadığı Bazı Kulüpler ve Ligler (Player Club Stats):")
    for s in stats:
        team_name = s.team.name if s.team else "Bilinmiyor"
        comp_name = s.competition.name if s.competition else "Bilinmiyor"
        print(f" - Sezon {s.season} | {team_name} | {comp_name} | {s.goals} Gol, {s.assists} Asist")
        
    print("-" * 50)
    
    # Transferler
    transfers = db.query(PlayerTransfer).filter_by(player_id=test_player.id).limit(5).all()
    print("Transfer Geçmişi:")
    for t in transfers:
        from_t = t.from_team.name if t.from_team else "Bilinmiyor"
        to_t = t.to_team.name if t.to_team else "Bilinmiyor"
        print(f" - {t.transfer_date} | {from_t} -> {to_t} | Ücret: {t.transfer_fee}")
        
    print("-" * 50)
    
    # Kupalar
    honours = db.query(PlayerHonour).filter_by(player_id=test_player.id).limit(5).all()
    print("Kazandığı Bazı Kupalar:")
    for h in honours:
        t_name = h.team.name if h.team else "Bilinmiyor"
        c_name = h.competition.name if h.competition else "Bilinmiyor"
        print(f" - Sezon {h.season} | {c_name} | {t_name} ile kazandı")

    db.close()

if __name__ == "__main__":
    verify_data()
