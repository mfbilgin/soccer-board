# Sosyal Özellikler (Social & Leaderboards)

Oyuncuların birbirleriyle etkileşimini artıran sosyal özellikler. `backend/routers/social.py` üzerinden kısmen kodlanmıştır.

## 1. Global Liderlik Tablosu (kodlanmış, çalışır durumda)
`GET /api/social/leaderboard/global`, tüm kullanıcıları `rating`'e göre azalan sırayla listeler, ilk **50**'yi döner (`rank`, `username`, `rating`, `level`). Sayfalama yoktur, sabit 50 kayıtla sınırlıdır.

## 2. Arkadaşlık Sistemi (Friendships)

::: tip Düzeltildi
Daha önce burada, arkadaşlık isteklerinin kabul edilemediği (istek gönderme var ama kabul endpoint'i yok, `GET /api/social/friends` pratikte hep boş dönüyordu) belirtiliyordu. Bu düzeltildi: `POST /api/social/friends/accept` ve `POST /api/social/friends/reject` (`{"username": "..."}`, `add_friend` ile aynı şema) eklendi — `accept`, göndericiyle alıcı arasındaki `pending` kaydı `"accepted"`e çevirir; `reject` aynı kaydı siler.
:::

- **Arkadaş Ekleme:** Kullanıcı adıyla (`username`) istek gönderilir — GDD'deki "User#1234" tarzı benzersiz kullanıcı kodu **kullanılmaz**, doğrudan `username` alanı kullanılır (kesinleştirilmiş karar: ek bir "kullanıcı kodu" alanı eklenmeyecek, `username` zaten `unique=True`).
- **Özel Maça Davet Etme:** **(Kodlanmadı)** — arkadaş listesindeki çevrimiçi kişilere anlık maç daveti (push/WebSocket bildirimi) backend'de yok.

## 3. Liderlik Tabloları (Leaderboards)
- **Global Rating Tablosu:** Kodlanmış, yukarı bkz.
- **Haftalık XP Şampiyonları:** **(Kodlanmadı)** — `User` tablosunda haftalık/dönemsel XP takibi yapan bir alan yok, yalnızca kümülatif `xp` var. Eklenecekse ayrı bir `weekly_xp` sayacı ve haftalık sıfırlama görevi gerekir (bkz. [Rank/ELO](/guide/systems/ranking-elo)'daki haftalık lig sıfırlama görevine eklenebilir).
- **Arkadaşlar Arası Sıralama:** **(Kodlanmadı)** — arkadaş kabul akışı çalışmadığı için bu tablo da fiilen boş kalır; arkadaş kabul bug'ı düzeltildikten sonra `GET /api/social/leaderboard/friends` olarak eklenmesi önerilir (mevcut `get_friends`'in zaten yaptığı `rating`'e göre sıralamayı kullanır).

## 4. Kullanıcı Profili Gösterişi (Flexing)
**(Kodlanmadı)** — favori kulüp, desteklenen milli takım, toplam maç sayısı gibi alanlar `User` tablosunda yok. `Win-Rate`/`Win Streak` gibi istatistikler için de ayrı bir `match_history` tablosu gerekir. Şu an maç olayları veritabanına değil, yalnızca oda başına bir dosyaya yazılıyor: `log_match_event` (`backend/routers/multiplayer.py`) her olayı `match_logs/{room_id}.jsonl` dosyasına satır satır ekliyor — bu, kalıcı/sorgulanabilir bir maç geçmişi değil, yalnızca teşhis amaçlı bir log dosyasıdır.
