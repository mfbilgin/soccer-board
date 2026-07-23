# Sosyal Özellikler (Social & Leaderboards)

Oyuncuların birbirleriyle etkileşimini artıran sosyal özellikler. `backend/routers/social.py` üzerinden kısmen kodlanmıştır.

## 1. Global Liderlik Tablosu (kodlanmış, çalışır durumda)
`GET /api/social/leaderboard/global`, tüm kullanıcıları `rating`'e göre azalan sırayla listeler, ilk **50**'yi döner (`rank`, `username`, `rating`, `level`). Sayfalama yoktur, sabit 50 kayıtla sınırlıdır.

## 2. Arkadaşlık Sistemi (Friendships)

::: danger Kısmen kodlanmış — istek kabul etme endpoint'i yok
- `POST /api/social/friends/add` (`{"username": "..."}`) çalışır: hedef kullanıcıyı bulur, kendine istek atmayı ve tekrar isteği engeller, `Friendship(status="pending")` satırı oluşturur.
- `GET /api/social/friends`, yalnızca `status == "accepted"` olan kayıtları döner.
- **Ama `status`'ü `"pending"`'den `"accepted"`'e çeviren hiçbir endpoint kodda yok.** Sonuç: bir arkadaşlık isteği gönderilebilir ama hiçbir zaman kabul edilemez, `GET /api/social/friends` pratikte **her zaman boş liste** döner.

**Kesin düzeltme:** `POST /api/social/friends/accept` (`{"username": "..."}`) endpoint'i eklenmeli — istek gönderenle alıcı arasındaki `pending` kaydı bulup `status = "accepted"` yapmalı. Reddetme için de `POST /api/social/friends/reject` (kaydı siler) eklenmelidir.
:::

- **Arkadaş Ekleme:** Kullanıcı adıyla (`username`) istek gönderilir — GDD'deki "User#1234" tarzı benzersiz kullanıcı kodu **kullanılmaz**, doğrudan `username` alanı kullanılır (kesinleştirilmiş karar: ek bir "kullanıcı kodu" alanı eklenmeyecek, `username` zaten `unique=True`).
- **Özel Maça Davet Etme:** **(Kodlanmadı)** — arkadaş listesindeki çevrimiçi kişilere anlık maç daveti (push/WebSocket bildirimi) backend'de yok.

## 3. Liderlik Tabloları (Leaderboards)
- **Global Rating Tablosu:** Kodlanmış, yukarı bkz.
- **Haftalık XP Şampiyonları:** **(Kodlanmadı)** — `User` tablosunda haftalık/dönemsel XP takibi yapan bir alan yok, yalnızca kümülatif `xp` var. Eklenecekse ayrı bir `weekly_xp` sayacı ve haftalık sıfırlama görevi gerekir (bkz. [Rank/ELO](/guide/systems/ranking-elo)'daki haftalık lig sıfırlama görevine eklenebilir).
- **Arkadaşlar Arası Sıralama:** **(Kodlanmadı)** — arkadaş kabul akışı çalışmadığı için bu tablo da fiilen boş kalır; arkadaş kabul bug'ı düzeltildikten sonra `GET /api/social/leaderboard/friends` olarak eklenmesi önerilir (mevcut `get_friends`'in zaten yaptığı `rating`'e göre sıralamayı kullanır).

## 4. Kullanıcı Profili Gösterişi (Flexing)
**(Kodlanmadı)** — favori kulüp, desteklenen milli takım, toplam maç sayısı gibi alanlar `User` tablosunda yok. `Win-Rate`/`Win Streak` gibi istatistikler için de ayrı bir `match_history` tablosu gerekir. Şu an maç olayları veritabanına değil, yalnızca oda başına bir dosyaya yazılıyor: `log_match_event` (`backend/routers/multiplayer.py`) her olayı `match_logs/{room_id}.jsonl` dosyasına satır satır ekliyor — bu, kalıcı/sorgulanabilir bir maç geçmişi değil, yalnızca teşhis amaçlı bir log dosyasıdır.
