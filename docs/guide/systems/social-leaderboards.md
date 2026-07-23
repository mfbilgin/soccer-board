# Sosyal Özellikler (Social & Leaderboards)

Oyuncuların birbirleriyle etkileşimini artıran sosyal özellikler.

## 1. Global Liderlik Tablosu
`GET /api/social/leaderboard/global`, tüm kullanıcıları rating'e göre azalan sırayla listeler, ilk **50**'yi döner (`rank`, `username`, `rating`, `level`). Sayfalama yoktur, sabit 50 kayıtla sınırlıdır.

## 2. Arkadaşlık Sistemi (Friendships)
- **Arkadaş Ekleme:** Kullanıcı adıyla (`username`) istek gönderilir; hedef kullanıcıya kendine istek atma ve tekrar istek engellenir. İstek `"pending"` durumunda oluşturulur.
- **Kabul/Red:** İstek alan taraf kabul veya reddedebilir; kabul edilen istek `"accepted"` durumuna geçer ve iki yönlü arkadaşlık listesinde görünür hale gelir; reddedilen istek silinir.
- Benzersiz "kullanıcı kodu" (User#1234 gibi) kullanılmaz, doğrudan `username` alanı kullanılır (zaten `unique`).
- **Özel Maça Davet Etme:** Arkadaş listesindeki çevrimiçi kişilere anlık maç daveti (push/WebSocket bildirimi). *Durum: kodlanmadı.*

## 3. Liderlik Tabloları (Leaderboards)
- **Global Rating Tablosu:** Yukarıda anlatıldığı gibi kodlanmıştır.
- **Haftalık XP Şampiyonları:** *Durum: kodlanmadı.* Kullanıcı kaydında haftalık/dönemsel XP takibi yapan bir alan yoktur, yalnızca kümülatif toplam XP tutulur. Eklenecekse ayrı bir `weekly_xp` sayacı ve haftalık sıfırlama görevi gerekir (bkz. [Rank/ELO](/guide/systems/ranking-elo)'daki haftalık lig sıfırlama görevine eklenebilir).
- **Arkadaşlar Arası Sıralama:** *Durum: kodlanmadı.* `GET /api/social/leaderboard/friends` olarak eklenmesi, arkadaş listesini rating'e göre sıralayarak döndürmesi önerilir.

## 4. Kullanıcı Profili Gösterişi (Flexing)
*Durum: kodlanmadı.* Favori kulüp, desteklenen milli takım, toplam maç sayısı gibi alanlar kullanıcı kaydında yoktur. `Win-Rate`/`Win Streak` gibi istatistikler için ayrı bir `match_history` tablosu gerekir — maç sonuçlarının veritabanına kalıcı olarak yazılması gerekir; şu an yalnızca oda başına, teşhis amaçlı bir log dosyasına (`match_logs/{room_id}.jsonl`) yazılır, sorgulanabilir/kalıcı bir maç geçmişi değildir.
