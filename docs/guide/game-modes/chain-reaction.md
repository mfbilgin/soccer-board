# Oyuncular-Takımlar Örgüsü Modu — "Zincir Oyunu"

2 veya daha fazla kişinin aynı lobide oynayabildiği, "Kelime Zinciri" oyununun futbol dünyasına uyarlanmış, hızlı ve eğlenceli bir eleme modudur.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki tasarım GDD'den (§3.10) alınmıştır. Yalnızca online (gerçek zamanlı çok oyunculu) olarak tasarlanmıştır.
:::

## Oyun Akışı
Oyun sırayla ilerler. Zincir her zaman "Oyuncu → Takım → Oyuncu → Takım" şeklinde devam etmek zorundadır.

1. Sistem ilk oyuncuyu seçer. 1. Oyuncu bir futbolcu söyler: **"Lionel Messi"**
2. Sıra 2. Oyuncuya geçer. Bu oyuncunun, Messi'nin kariyerinde oynadığı bir takımı söylemesi zorunludur. Cevap verir: **"Barcelona"**
3. Sıra (varsa) 3. Oyuncuya veya tekrar 1. Oyuncuya geçer. Bu oyuncunun, Barcelona'da forma giymiş (ancak Messi hariç, daha önce söylenmemiş) başka bir oyuncuyu söylemesi gerekir. Cevap verir: **"Ronaldinho"**
4. Sıra bir sonrakine geçer: Ronaldinho'nun oynadığı başka bir takım söylenmelidir: **"AC Milan"**

## Eleme ve Süre Kuralları
- **Tekrar Kuralı:** O maç içinde daha önce söylenmiş bir oyuncu veya takım tekrar söylenemez (oturum boyunca bir geçmiş listesi tutulur).
- **Süre Sınırı:** Sıra size geldiğinde cevap vermek için sadece **15 saniyeniz** vardır.
- 15 saniye içinde doğru, kurallara uyan ve daha önce söylenmemiş bir cevap veremeyen oyuncu **elenir**.
- Elenenler izleyici olur. Masada **son 1 kişi** kalana kadar oyun devam eder ve o kişi turun galibi olur.

## Kısıtlamalar ve Uç Durumlar
- **Geçerlilik doğrulaması:** Söylenen oyuncunun gerçekten o takımda oynayıp oynamadığı (`player_club_stats`/`player_transfers` üzerinden) veritabanı ile anında doğrulanmalıdır.
- **Tekrar kontrolü:** Oturum geçmişi (o maçta daha önce söylenen tüm oyuncu/takım ID'leri) backend'de tutulmalı, istemciye güvenilmemelidir.
- **İtiraz mekanizması gerekmez:** Sistem otoritedir — cevap veritabanına göre doğru/yanlış kabul edilir, oyuncular arası itiraz mekanizmasına ihtiyaç yoktur.
- **"Açık uç" riski:** Zincir bir noktada çözümsüz kalabilir (o takımda oynamış, daha önce söylenmemiş kimse kalmayabilir). *(Tasarım Kararı: sistem her adımda en az bir geçerli devam seçeneğinin var olduğunu bilmeli; çözümsüz bir noktaya gelinirse tur sıfırlanır/yeni bir başlangıç noktasıyla yeniden başlar.)*

## Olası Backend İhtiyaçları (tasarım aşaması)
- Multiplayer WebSocket altyapısına (`routers/multiplayer.py`, `socket_manager.py`) 2+ kişilik lobi desteği eklenmesi gerekir — `Room` sınıfının kendisi oyuncu sayısını sınırlamıyor, ama eşleştirme kuyruğu ve kazanan/kaybeden (`winner_id`/`loser_id`) tabanlı skor/rating mantığı şu an 1v1 için tasarlanmış; N-kişilik elemeli bir moda uyarlanması gerekir.
- Her tur için "söylenen oyuncu/takım geçerli mi ve zincire uyuyor mu" kontrolünü yapan bir doğrulama fonksiyonu (`player_club_stats` ve `player_transfers` tablolarını birlikte kullanmalı, çünkü bir oyuncu bir takımda kısa süre kiralık oynamış da olabilir).
