# Backend (FastAPI & WebSockets)

Backend sistemi, yüksek performanslı ve asenkron Python framework'ü olan FastAPI üzerine inşa edilmiştir.

## REST API (routers/)
Tüm HTTP endpoint'leri `routers` klasörü altında mantıksal olarak ayrılmıştır. `main.py`'de kayıtlı gerçek router'lar:
- **auth.py:** Kullanıcı kaydı, girişi (JWT tabanlı) işlemlerini barındırır.
- **game.py** (`/api/game/tictactoe`): TicTacToe grid oluşturma (`/grid`), oyuncu tahminlerini doğrulama (`/guess`), pes etme (`/surrender`) ve oyuncu/takım arama (`/search`).
- **target_score.py** (`/api/mode31`): "Kariyer İstatistiği Avı" (Target Score) modu — bulmaca üretme (`/generate`) ve tahmin doğrulama (`/validate-single`, `/validate`).
- **pyramid.py** (`/api/game/pyramid`): İsminin aksine [Piramit Sıralaması](/guide/game-modes/pyramid-ranking) değil, [Top 10 Tahmin](/guide/game-modes/top-10-guess) modu için içerik üretir (`/generate`).
- **career_guess.py** (`/api/game/career-guess`): Transfer geçmişinden oyuncu tahmini — bulmaca üretme (`/generate`) ve doğrulama (`/verify`).
- **social.py** (`/api/social`): Global liderlik tablosu ve arkadaşlık istekleri.
- **multiplayer.py** (`/api/multiplayer` + `ws_router`): Oda/eşleştirme REST uçları ve WebSocket bağlantı noktası (`/api/multiplayer/ws`).
- Ayrıca `main.py` içinde doğrudan tanımlı `/api/players/search` (genel oyuncu arama) endpoint'i vardır.

::: info Kapsam notu
Şu an yalnızca **TicTacToe, Target Score, Pyramid ve Career Guess** modlarının hem backend router'ı hem frontend ekranı mevcut. Diğer modlar (bkz. [Game Modes](/guide/game-modes/stats-target)) tasarım dokümanı aşamasında, henüz kodlanmadı.
:::

## Gerçek Zamanlı Eşleşme (routers/multiplayer.py + socket_manager.py)
Multiplayer tarafı tamamen WebSockets üzerine kuruludur. `multiplayer.py` içindeki `ws_router` (`/api/multiplayer/ws`) endpoint'i ve oyun döngüsünü barındırır; oda/bağlantı durumu ise `socket_manager.py`'deki `ConnectionManager` (`manager` tekil nesnesi, `Room` sınıfı) tarafından tutulur. Birlikte şunlardan sorumludurlar:
1. **Lobi Yönetimi:** Kullanıcıların odalara (Room) katılması.
2. **Eşleştirme (Matchmaking):** Aynı seviyedeki oyuncuların birbirleriyle eşleştirilmesi.
3. **Oyun Döngüsü Senkronizasyonu:** Bir oyuncu tahtada bir hamle (örneğin X yerleştirdiğinde) yaptığında anında diğer oyuncuya iletilmesi ve tahtanın güncellenmesi.
4. **Ekonomi Entegrasyonu:** `services/economy.py` üzerinden giriş ücreti kesme (`deduct_entry_fee`), kazanana ödül dağıtma (`award_winnings`, %10 rake ile) ve bağlantı kopmasında hükmen mağlubiyet (`process_forfeit`).

## Ekonomi Servisi (services/economy.py)
Chip/XP/Rating hesaplamalarını merkezi olarak yönetir: `deduct_entry_fee`, `award_winnings`, `add_xp_and_check_level` (Level formülü: `XP = 100 * level^1.5`) ve `update_rating` (standart Elo, K=32). Detaylar için [Gems & Chips](/guide/systems/economy-gems-chips) ve [Rank/ELO](/guide/systems/ranking-elo).
