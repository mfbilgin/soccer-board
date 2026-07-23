# Tüm Modlar İçin Ortak Multiplayer (Online) Sistemi

Tüm online oyun modları (İstatistik Hedefleri, Tic-Tac-Toe vb.) temel bir eşleştirme ve oda (Room) altyapısı üzerine kuruludur. Bu sayede her mod için ayrı ayrı eşleştirme yazmak yerine merkezi bir sistem kullanılır.

## 1. Odalar ve Giriş Ücretleri (Tiers)
Oyuncular bir oyun modunu online oynamak istediklerinde karşılarına `RoomSelectionScreen.js` ekranı çıkar. Odalar, oyuncuların bütçesine göre ayrılmıştır:
- **Örnek Odalar:** Acemi Odası (100 Chip Giriş), Profesyonel Odası (10.000 Chip Giriş), Efsane Odası (500.000 Chip Giriş) vb.
- Oyuncunun hesabında yeterli Chip (bakiye) yoksa o odaya giremez.

## 2. Eşleştirme Sistemi (Matchmaking)
Sistem (Backend Socket), eşleştirmeleri iki ana kritere göre yapar:
1. **Oda (Giriş Ücreti):** Sadece aynı oyun modunda, aynı giriş miktarına sahip odayı seçmiş kullanıcılar birbirleriyle eşleşebilir.
2. **Rating (Elo) Yakınlığı:** Sistemin adil olması için eşleşen oyuncuların "Rating" (Elo/Yetenek Puanı) değerleri birbirine yakın olmalıdır. Ancak eşleştirme süresi uzadıkça, oyuncuları bekletmemek adına Rating makası (fark toleransı) zamanla kademeli olarak genişler.

## 3. Oyun İçi Kullanıcı Arayüzü (UI)
Online maç başladıktan sonra, tüm oyun modlarında ekranın en üstünde standart bir oyuncu HUD'ı (Göstergesi) bulunur:
- **Sol Üst:** Kendi oyuncu kartınız.
- **Sağ Üst:** Rakibin oyuncu kartı.
- **Kart İçeriği:** Kullanıcının avatarı, avatarın sağ üstünde seviyesi (Level) ve hemen altında kullanıcı adı yer alır.

## 4. Oyuncu Profili Modalı (Stat Gösterimi)
Oyun sırasında (veya lobi anında) rakibin veya kendi kartınızın üzerine tıklandığında bir Modal açılır. Bu ekranda oyuncuya ait detaylı rekabetçi istatistikler listelenir:
- Toplam Oynadığı Oyun Sayısı
- Kazanma Oranı (Win Rate - %)
- Mevcut Galibiyet Serisi (Win Streak)
- vb.

## 5. Bağlantı Kopması ve Hükmen Mağlubiyet (Disconnection)
Online oyun doğası gereği bağlantı sorunları yaşanabilir.
- Bir oyuncu oyunu kapatırsa, uygulamayı arka plana atarsa veya internet bağlantısı koparsa oyun **anında duraklatılır**.
- Oyunda kalan kişinin ekranında *"Rakibin bağlantısı koptu, yeniden bağlanması bekleniyor..."* şeklinde bir ibare ve geri sayım belirir.
- Kopan oyuncuya oyuna dönmesi için **30-45 saniye** arası bir süre tanınır.
- Bu süre içinde yeniden bağlanmazsa, kopan oyuncu **Hükmen Mağlup (Forfeit)** sayılır. Oyunda kalan oyuncu odayı galip olarak tamamlar ve giriş ücretine tekabül eden ödülü kazanır. Backend tarafında bu akış `services/economy.py`'deki `process_forfeit` fonksiyonuyla yürütülür.

## 6. Ödül Havuzu, Rake ve Beraberlik Kuralı
- **Ödül havuzu:** Odaya giren tüm oyuncuların giriş ücretlerinin toplamıdır (Örn: 2 kişi 500'er Chip yatırdı = 1000 Chip havuz).
- **Rake (sistem komisyonu):** Kazanan, havuzun **%90'ını** alır; **%10'u sistem kesintisidir**. Bu oran backend'de `services/economy.py` içindeki `RAKE_PERCENTAGE = 0.10` sabitiyle uygulanır (`award_winnings` fonksiyonu).
- **Beraberlik / kazanan yok:** Hiçbir oyuncu kazanma koşulunu sağlamazsa (örn. süre dolduğunda ikisi de doğru cevap veremezse), oda ücretleri **iade edilir ve rake kesilmez** — bu kural oyuncu güvenini korumak için tasarlanmıştır. *(Tasarım Kararı — GDD §3, "Ortak Online Kurallar".)*
- **Zamanlayıcı otoritesi:** Tüm tur bazlı modlarda süre backend'de (sunucuda) tutulur; istemci yalnızca geri sayımı gösterir, süreyi kendisi belirlemez — bu, süre hile/manipülasyonunu engeller.
