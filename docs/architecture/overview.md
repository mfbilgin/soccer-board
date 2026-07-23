# Mimari Genel Bakış (Overview)

Bu sayfa projenin klasör yapısını, katmanlarını ve tasarım prensiplerini anlatır. Sistemin bileşenleri ve veri akışı için [Genel Mimari](/guide/architecture) sayfasına bakın — bu ikisi birbirini tamamlar: o sayfa "hangi parçalar var", bu sayfa "kod nasıl organize edilmiş ve neden".

## Klasör Yapısı

```
project/
├── backend/                 # FastAPI uygulaması
│   ├── main.py               # Uygulama girişi, router kaydı, startup cache init
│   ├── models.py              # SQLAlchemy ORM modelleri (tek kaynak — bkz. database.md)
│   ├── schemas.py             # Pydantic request/response şemaları (kısmen kullanılıyor, bkz. decisions/003-api.md)
│   ├── database.py            # Engine/SessionLocal, DATABASE_URL_V2 okuma
│   ├── security.py            # JWT + bcrypt (bkz. decisions/001-auth.md)
│   ├── socket_manager.py      # ConnectionManager + Room — tüm WS oda/kuyruk durumu
│   ├── tictactoe.py           # TicTacToeEngine — takım/oyuncu kesişim önbelleği (diğer motorlarca da paylaşılır)
│   ├── chain_reaction.py      # ChainReactionEngine
│   ├── find_two.py            # FindTwoEngine
│   ├── initials_guess.py      # InitialsGuessEngine
│   ├── routers/                # Her mod/özellik için bir router dosyası
│   │   ├── auth.py, game.py, pyramid.py, target_score.py, career_guess.py,
│   │   │   extreme_squad.py, flag_eleven.py, initials_guess.py, social.py
│   │   └── multiplayer.py     # WS endpoint + tüm online modların oyun döngüsü
│   ├── services/economy.py    # Chip/XP/rating hesaplamaları (tüm modlarca paylaşılır)
│   └── scripts/                # Tek seferlik/idempotent bakım script'leri (bkz. database.md)
├── frontend/                 # Expo (React Native) uygulaması
│   ├── App.js                  # Navigation kurulumu (bkz. architecture/frontend.md)
│   ├── api.js                   # axios instance + token interceptor
│   ├── services/SocketService.js # Tekil WebSocket istemcisi
│   ├── screens/auth|main|singleplayer|multiplayer/
│   ├── components/             # SearchModal, CustomTabBar, UpdateOverlay
│   └── theme.js                 # Renk/font/boyut sabitleri
├── scraper_bot/               # Bağımsız veri toplama script'i
│   ├── distributed_scraper.py  # TMAPI/CEAPI'den çekip backend'le AYNI Postgres'e yazar
│   └── models_v2.py             # backend/models.py'nin ayrı bir kopyası (bkz. Bilinen Sınırlamalar)
└── docs/                      # Bu VitePress dokümantasyonu
```

## Katmanlar

1. **İstemci (React Native ekranları)** — yalnızca görüntüleme ve kullanıcı girdisi; iş kuralı barındırmaz.
2. **Transport** — REST (axios, `/api/...`) tek seferlik istekler için; WebSocket (`SocketService`, `/api/multiplayer/ws`) canlı oyun durumu için. İkisi ayrı taşıma katmanı olarak bilinçli şekilde ayrılmıştır (bkz. [ADR 003](/decisions/003-api)).
3. **Router / oyun motoru (backend)** — HTTP endpoint'leri (`routers/*.py`) veya WS action handler'ları (`routers/multiplayer.py`) isteği karşılar; oyuna özel kurallar ayrı bir "engine" sınıfında/fonksiyonunda yaşar (`tictactoe.py`, `chain_reaction.py`, `find_two.py`, `initials_guess.py`, `routers/extreme_squad.py`, `routers/flag_eleven.py`, `routers/pyramid.py`) — router fonksiyonları bu motorları çağırıp HTTP/WS'e uygun hale getirir.
4. **Ekonomi/ödül katmanı** — `services/economy.py`; her modun kazanan/kaybeden mantığı bu tek yerdeki `award_winnings`/`update_rating`/`add_xp_and_check_level` fonksiyonlarını çağırır, ödül hesaplama kuralı modlar arasında kopyalanmaz.
5. **Kalıcılık (Postgres)** — `models.py` tek şema kaynağıdır; tüm router'lar ve motorlar aynı tabloları okur/yazar.
6. **Bellek-içi durum (in-memory)** — canlı bir odanın durumu (`Room.game_state`) veritabanına hiç yazılmaz, yalnızca backend process'inin RAM'inde yaşar (bkz. Tasarım Prensipleri).

## Tasarım Prensipleri

- **Motor / router ayrımı:** Bir oyun modunun kuralları (bulmaca üretimi, doğrulama, "teorik en iyi" hesaplama gibi) her zaman HTTP/WS'ten bağımsız, test edilebilir bir fonksiyon/sınıfta yaşar. Router hem singleplayer HTTP endpoint'inden hem de `routers/multiplayer.py`'deki online akıştan **aynı fonksiyonu** çağırır — kural iki yerde ayrı ayrı yazılmaz (örnek: `extreme_squad.generate_puzzle`, `pyramid.generate_puzzle`, `chain_reaction.ChainReactionEngine`).
- **Sunucu otoritedir, istemciye güvenilmez — ama seçici olarak:** Bir bulmacanın *cevabı* asla istemciye önceden gönderilmez (bkz. `flag_eleven.py`'deki `PUZZLES` önbelleği, `top10`'un `_top10_public_items` ile gizli hücreleri kırpması). Ancak bazı ara hesaplamalarda (örn. `target_score.py`/`extreme_squad.py`'nin `validate` uç noktaları) istemcinin geri gönderdiği puzzle parametrelerine güvenilir — bu bilinçli bir basitlik/güvenlik ödünleşimidir, her yeni mod eklerken hangi tarafta durduğuna karar verilmelidir.
- **Migrasyon çerçevesi yok, idempotent script var:** Şema değişiklikleri Alembic gibi bir araçla değil, elle yazılmış `ADD COLUMN IF NOT EXISTS` script'leriyle yapılır (bkz. [Database Structure](/architecture/database)). Veri onarım/backfill script'leri her zaman "hâlâ bozuk olan satırları hedefle" prensibiyle yazılır ki kesintiye uğrarsa güvenle tekrar çalıştırılabilsin.
- **Önbellek, kalıcılık değildir:** `TicTacToeEngine._CACHE`, `InitialsGuessEngine._CACHE`, `flag_eleven.PUZZLES` gibi modül-seviyesi sözlükler yalnızca process ömrü boyunca yaşar. Backend yeniden başladığında veya birden fazla process/worker çalıştırıldığında bu önbellekler paylaşılmaz — bkz. Bilinen Sınırlamalar.
- **Minimal soyutlama:** Ortak bir desen (örn. best-of-5 buzzer maçı) iki modda tekrar ediyorsa bile, üçüncü bir mod gelene kadar erken bir "BuzzerMatch" soyutlaması çıkarılmaz — `find_two.py`, `initials_guess.py` ve `flag_eleven`'in online akışı bilinçli olarak birbirinden bağımsız, küçük tekrarlarla yazılmıştır.

## Bilinen Sınırlamalar

- `scraper_bot/models_v2.py`, `backend/models.py`'nin bağımsız bir kopyasıdır (aynı tabloları farklı bir SQLAlchemy `Base`'le tanımlar). Birine kolon eklerken diğeri unutulursa scraper veya backend sessizce eksik veri yazar/okur (bu session'da `height_cm` eklenirken ikisi de güncellendi — yeni kolon eklerken bu ikiliyi hatırlamak gerekir).
- WS oda durumu tek process'in RAM'inde tutulur; yatay ölçeklenme (birden fazla backend instance'ı) için Redis gibi paylaşımlı bir store gerekir — şu an tek instance varsayımıyla çalışılıyor.
