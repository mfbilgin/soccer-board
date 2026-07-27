# Backend Mimarisi

Hangi router'ın ne yaptığı için [Backend (FastAPI & WebSockets)](/guide/backend) sayfasına bakın. Burası klasör yapısına, katmanlara ve mimari tercihlerin *neden*ine odaklanır.

## Klasör Yapısı

```
backend/
├── main.py                  # FastAPI() + router kaydı + startup cache init
├── models.py                  # SQLAlchemy ORM şeması (tek gerçek kaynak)
├── schemas.py                  # Pydantic şemaları (kısmen kullanılır — bkz. Tasarım Prensipleri)
├── database.py                  # engine, SessionLocal, get_db, DATABASE_URL_V2
├── security.py                  # JWT + bcrypt (bkz. ADR 001)
├── socket_manager.py            # ConnectionManager (manager) + Room — tüm oda/kuyruk durumu (oyun kurallarından habersiz)
├── tictactoe.py, chain_reaction.py, find_two.py, initials_guess.py
│                                # Motor sınıfları — HTTP/WS'ten bağımsız oyun mantığı
├── games/                       # Online oyun modları (Strategy + Registry deseni)
│   ├── base.py                  # GameMode ABC: start/actions/on_surrender/on_abandon sözleşmesi
│   ├── registry.py              # @register dekoratörü + get_game(mode)
│   ├── lifecycle.py             # Ortak yardımcılar: log, timer döngüleri, ödeme, oda temizliği
│   └── target_score.py, top10.py, tictactoe.py, chain_reaction.py, ...
│                                # Mod başına bir GameMode alt sınıfı
├── routers/
│   ├── auth.py, social.py
│   ├── game.py, pyramid.py, target_score.py, career_guess.py,
│   │   extreme_squad.py, flag_eleven.py, initials_guess.py
│   │                            # Her mod için: puzzle üretimi + doğrulama endpoint'leri
│   └── multiplayer.py           # İnce WS girişi: auth + kuyruk/lobi + games/ registry'sine dispatch
├── services/economy.py          # deduct_entry_fee, award_winnings, update_rating, add_xp_and_check_level
└── scripts/                     # Idempotent bakım/backfill script'leri (bkz. database.md)
```

## Katmanlar

1. **Router (HTTP)** — `routers/*.py`; her biri kendi `APIRouter(prefix=...)`'ını tanımlar, `main.py`'de `app.include_router(...)` ile kaydedilir.
2. **WS dispatcher (`routers/multiplayer.py`)** — tek bir `@ws_router.websocket("/api/multiplayer/ws")` endpoint'i (bkz. [ADR 003](/decisions/003-api)). Kuyruk/lobi aksiyonlarını kendisi işler; oyun içi her aksiyonu `games.get_game(room.game_mode).handle_action(...)` ile ilgili moda yönlendirir. Oyun kuralları bu dosyada yaşamaz.
3. **Oyun modu katmanı (`games/`)** — her online mod, `GameMode` sözleşmesini (`start`, `actions`, `on_surrender`, `on_abandon`) uygulayan bir sınıftır ve `@register` ile registry'ye kaydolur. Ortak davranış (tur sayacı, maç sonu ödemesi, oda temizliği, maç logu) `games/lifecycle.py`'dedir. Yeni mod eklemek = `games/` altına yeni modül + `games/__init__.py` import listesine bir satır; router'a ve `socket_manager`'a dokunulmaz.
4. **Motor (engine)** — bir modun kuralları HTTP/WS'ten tamamen bağımsız yaşar: `generate_puzzle(db)`, `validate_guess(...)` gibi saf fonksiyonlar/sınıflar. Hem singleplayer router hem `games/` altındaki mod sınıfı **aynı** motoru çağırır.
5. **Ekonomi (`services/economy.py`)** — kazanç/rating/XP hesabı tek yerde; her mod kendi ödül matematiğini yazmaz. WS katmanı için kendi DB oturumunu yöneten `*_safe` sarmalayıcıları da buradadır.
6. **Kalıcılık (Postgres)** — `models.py` + `database.SessionLocal`.
7. **Bellek-içi durum** — `socket_manager.Room.game_state` (canlı bir maçın anlık durumu) ve modül-seviyesi önbellekler (`tictactoe._CACHE`, `initials_guess._CACHE`, `flag_eleven.PUZZLES`) — hiçbiri veritabanına yazılmaz.

## Tasarım Prensipleri

- **Tek WS endpoint, action-bazlı yönlendirme.** Her mod için ayrı bir WebSocket rotası açmak yerine tüm online modlar aynı `/api/multiplayer/ws` bağlantısını, mesajın `action` alanıyla paylaşır. Oda/kuyruk altyapısı (`socket_manager.py`) tüm modlarda ortaktır; oyuna özel davranış odanın `game_mode`'una kayıtlı `GameMode` sınıfındadır.
- **Bağımlılık yönü hep games → socket_manager.** `socket_manager` oyun katmanını import etmez; oyuna gitmesi gereken olaylar (`on_match_start`, `on_player_abandon`) `games/__init__.py`'nin startup'ta enjekte ettiği kancalarla akar (Dependency Inversion). Eski döngüsel `from routers.multiplayer import ...` lazy-import'ları kaldırılmıştır.
- **Motor / endpoint ayrımı zorunlu.** Yeni bir mod eklerken önce motor (üretim + doğrulama, DB'den bağımsız test edilebilir) yazılır, sonra ince bir HTTP router ve/veya `games/` altındaki mod sınıfı bu motoru çağırır. Bu sayede singleplayer ve online aynı kuralı paylaşır (bkz. `extreme_squad.generate_puzzle`'ın hem `/generate` hem `ExtremeSquadGame.start`'tan çağrılması).
- **Cevap asla erken ifşa edilmez.** `flag_eleven.py`'nin `PUZZLES` önbelleği ve `Top10Game._public_items` gibi yardımcılar, doğru cevabı yalnızca sunucu tarafında tutar; istemciye giden JSON'da hiçbir zaman "gizli" alan bulunmaz. Yeni bir mod yazarken ilk soru: *"cevabı istemciye önceden göndersem oyun bozulur mu?"* — cevap evetse, motor "genel görünüm" (public view) üretmelidir.
- **Self-cancel edilebilir timer görevleri.** Her online modun tur/süre sayacı (`asyncio.create_task`) `room.game_state["timer_task"]`'te saklanır; bir tur biterken bu görev kendi kendini `.cancel()` edebilir (Python'da bir task'ın kendini iptal etmesi güvenlidir, sıradaki `await` noktasında `CancelledError` fırlatılır ve yutulur). Döngü mantığı `games/lifecycle.py`'deki `run_turn_timer` / `run_countdown` içinde tek yerde yaşar; her mod yalnızca timeout callback'ini verir.
- **Pydantic şemaları tutarlı kullanılmaz — bilinçli bir eksiklik.** `schemas.py`'deki `response_model`'ler yalnızca en eski endpoint'lerde (`game.py`'nin grid/guess/search'ü, `auth.py`) kullanılıyor; yeni modların çoğu ham `dict` döner. Yeni bir endpoint yazarken hangisini seçeceğiniz konusunda bir kural yok — mevcut komşu router'ın deseni takip edilir.

## Bilinen Sınırlamalar

- ~~`routers/multiplayer.py` art arda eklenen `elif action == "..."` dallarıyla büyüyor~~ — çözüldü: online modlar `games/` paketine mod-başına sınıflara bölündü; router yalnızca dispatch yapar.
- Modül-seviyesi önbellekler (`_CACHE`, `PUZZLES`) hiç boşaltılmaz/TTL'siz büyür; uzun süre çalışan bir process'te bellek kullanımı yavaşça artar (özellikle `flag_eleven.PUZZLES` — bir kullanıcı bulmacayı hiç bitirmeden uygulamadan çıkarsa o giriş sonsuza kadar kalır).
