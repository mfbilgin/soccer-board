# Yol Haritası (Roadmap)

Bu sayfa "sırada ne var" sorusuna cevap verir; anlık iş durumu için [current-task.md](/current-task) sayfasına bakın (o sayfa zamanla değişir, bu sayfa daha kalıcı bir öncelik sırasıdır).

## Tamamlanan Büyük Kilometre Taşı: 10 Oyun Modu

`taslak_plan.txt`'te tasarlanan **10 oyun modunun tamamı** artık kodlanmış ve çalışır durumda (bkz. [Game Modes](/guide/game-modes/stats-target) sidebar'ı): İstatistik Hedefleri, En X Kadroyu Kur, 4x4 TicTacToe, Top 10 Tahmin (online dahil), 2 Takım/Ülkeden Bul, Transferlerden Tahmin, Piramit Sıralaması, Baş Harflerinden Bul, Bayraklarla İlk 11, Oyuncular-Takımlar Örgüsü. Odak artık **yeni mod eklemekten**, ekonomi/sosyal katmanı tamamlamaya ve teknik borcu azaltmaya kayıyor.

## Sıradaki Öncelikler

### 1. Ekonomi ve Sosyal Katmanı (spec hazır, kodlanmadı)
`docs/guide/systems/*` sayfalarının her biri "Durum: kodlanmadı" ile işaretli, uygulanabilir kesin speclere sahip:
- **IAP (gerçek para ile gem satın alma)** — App Store/Play Store satın alma doğrulama akışı gerekir.
- **Haftalık/sezonluk lig ödülü** ve **ELO lig kümeleme (banding)** — `ranking-elo.md`'deki tasarıma göre; şu an yalnızca ham `rating` sayısı var, kümeleme yok.
- **Günlük giriş serisi (streak) ödülü** — `users` tablosuna `last_login_date`/`streak_count` alanı gerekir.
- **Avatar/market sistemi** — envanter tablosu + satın alma endpoint'i + [Profil ekranı](/features/profile) (şu an yalnızca boş bir tab).
- **2x XP/Chip takviyesi (boost)** — gems karşılığı süreli çarpan.
- **Arkadaşlar arası sıralama, haftalık XP şampiyonları, kalıcı maç geçmişi tablosu** — bkz. `social-leaderboards.md`; şu an maç sonuçları yalnızca teşhis amaçlı `match_logs/*.jsonl` dosyalarına yazılıyor, sorgulanabilir bir tabloya değil.

### 2. Bildirimler
Hiç kodlanmadı (bkz. [features/notifications.md](/features/notifications)). En yüksek fayda: maç bulundu push bildirimi (kullanıcı kuyruktayken uygulama arka plandaysa).

### 3. Bilinen Teknik Borç
- `security.py`'deki `SECRET_KEY` ortam değişkenine taşınmalı (bkz. [ADR 001](/decisions/001-auth)).
- `LoginScreen.js`'in jenerik hata mesajı (ağ hatası ile yanlış şifreyi ayırt etmiyor).
- `routers/multiplayer.py` büyüyor; bir sonraki modda mod-başına dosyalara bölünmesi değerlendirilmeli (bkz. [ADR 003](/decisions/003-api)).
- Modül-seviyesi önbellekler (`flag_eleven.PUZZLES` gibi) TTL'siz büyüyor.
- `scraper_bot/models_v2.py` ile `backend/models.py`'nin manuel senkron tutulması gerekiyor (bkz. [architecture/database.md](/architecture/database)).

### 4. Devam Eden Veri Kalitesi İşleri
Takım isimlerindeki karmaşayı gidermek için başlatılan arka plan işleri (bkz. [current-task.md](/current-task)):
- Takım profili backfill'i (placeholder isim + eksik ülke onarımı).
- `players.height_cm` backfill'i — tamamlanınca Extreme Squad'ın `tallest` kriteri her zaman kullanılabilir hale gelecek (şu an yetersiz veri varsa `youngest`'e otomatik düşüyor).

## Kapsam Dışı (Şimdilik)

- Gerçek zamanlı sesli/görüntülü sohbet.
- Turnuva modu (`LobbyScreen.js`'te bir yer tutucu kart var, `active: false`).
- Web/masaüstü istemcisi — yalnızca iOS/Android (Expo) hedefleniyor.
