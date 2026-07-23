# Frontend Mimarisi

Ne olduğu ve nasıl çalıştığı için [Frontend (React Native & Expo)](/guide/frontend) sayfasına bakın. Burası klasör yapısına, katmanlara ve mimari tercihlerin *neden*ine odaklanır.

## Klasör Yapısı

```
frontend/
├── App.js                        # Tek navigation kökü: Stack + alt Tab navigator
├── api.js                         # axios instance, DROPLET_IP/API_URL, token interceptor
├── theme.js                       # COLORS/SIZES/FONTS/GLOBAL_STYLES sabitleri
├── services/
│   └── SocketService.js            # Tekil (singleton) WebSocket istemcisi
├── components/
│   ├── SearchModal.js              # Oyuncu/takım arama — 6 moddan fazlası tarafından paylaşılır
│   ├── CustomTabBar.js
│   └── UpdateOverlay.js            # EAS OTA güncelleme bildirimi
└── screens/
    ├── auth/                       # LoginScreen, RegisterScreen
    ├── main/                       # HomeScreen (alt tab: "Oyna")
    ├── singleplayer/                # Her offline mod için bir ekran
    └── multiplayer/                 # Lobby, RoomSelection + her online mod için bir ekran
```

## Katmanlar

1. **Ekran (screen) bileşenleri** — her ekran kendi yerel state'ini (`useState`) tutar; küresel bir state deposu yoktur (bkz. [ADR 002](/decisions/002-state-management)).
2. **Servis katmanı** — `api.js` (REST) ve `SocketService.js` (WS) ekranlarla backend arasındaki tek temas noktasıdır. Ekranlar hiçbir zaman doğrudan `fetch`/`WebSocket` çağırmaz.
3. **Navigasyon** — `@react-navigation/native-stack` (ekranlar arası geçiş) içinde bir `@react-navigation/bottom-tabs` (`MainTabs`) gömülüdür. Her yeni mod eklendiğinde `App.js`'e bir `Stack.Screen` eklenir; offline modlar ayrıca `SingleplayerScreen.js`'in `GAME_MODES` listesine, online modlar `LobbyScreen.js`'in `GAME_MODES` listesine ve `RoomSelectionScreen.js`'in yönlendirme `if/else`'ine eklenir — bu üç yer birlikte güncellenmezse mod menüde görünür ama tıklanamaz ya da hiç görünmez.

## Tasarım Prensipleri

- **Küresel state yönetimi yok, kasıtlı olarak.** Redux/Context/Zustand gibi bir kütüphane kullanılmaz; her ekran ihtiyaç duyduğu veriyi (`GET /api/auth/me` gibi) kendi `useEffect`'inde çeker. Bkz. [ADR 002](/decisions/002-state-management) — bunun bilinçli bir ödünleşim olduğu ve nerede acı verdiği orada anlatılıyor.
- **Tek WebSocket, çok mod.** `SocketService`, tüm online modlar için **tek** bir bağlantı açar; hangi mod olduğu bağlantı kurulduktan sonra `action` alanıyla ayrışır (bkz. [ADR 003](/decisions/003-api)). Ekranlar `SocketService.on(type, callback)` ile kendi ilgilendiği mesaj tiplerine abone olur.
- **Native WebSocket, socket.io değil.** `new WebSocket(...)` kullanılır (React Native'in yerleşik API'si); backend tarafında da FastAPI'nin native `WebSocket` desteği kullanılır — ekstra bir soket kütüphanesi/protokolü yoktur.
- **SearchModal tekrar kullanımı.** Oyuncu/takım aramak isteyen her ekran (TicTacToe, Extreme Squad, Find Two, Initials Guess, Top10, ...) aynı `components/SearchModal.js`'i, `searchType` prop'uyla (1 = oyuncu, 2 = takım) parametrize ederek kullanır — arama UI'ı her modda yeniden yazılmaz.
- **Ekranlar arası tutarlı görsel dil.** `theme.js`'teki `COLORS`/`FONTS`/`GLOBAL_STYLES` her ekranda kullanılır; yeni bir ekran yazarken renk/font hardcode edilmez.

## Bilinen Sınırlamalar

- Kullanıcı profili (chip/gem/xp/level/rating) her ekranda ayrı ayrı `GET /api/auth/me` ile çekilir — küresel bir "kullanıcı" state'i olmadığı için aynı veri birden fazla kez, birbirinden habersiz şekilde indirilir. Bkz. [ADR 002](/decisions/002-state-management) ve [profile.md](/features/profile).
- `LoginScreen.js`, ağ hatası/timeout/401 gibi farklı hata türlerini aynı jenerik "Giriş başarısız" mesajıyla gösterir — kullanıcıya yanlış teşhis verebilir (bkz. [current-task.md](/current-task)).
