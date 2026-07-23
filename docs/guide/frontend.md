# Frontend (React Native & Expo)

Kullanıcı arayüzü ve deneyimi React Native (Expo) kullanılarak geliştirilmiştir. 

## Dosya ve Klasör Yapısı
- **`screens/`**: Uygulamanın tüm sayfalarını barındırır (Auth, Home, Multiplayer, Singleplayer vb.)
- **`components/`**: Tekrar kullanılabilir UI elementleri (Button, GridCell, PlayerCard).
- **`navigation/`**: React Navigation kurgusunu içerir. Tab navigator ve Stack navigator ayarları buradadır.
- **`api.js`**: Axios konfigürasyonu, interceptor'lar ve backend istek fonksiyonları burada tanımlıdır.
- **`theme.js`**: Uygulama içi renk paletleri, font büyüklükleri ve modern glassmorphism tarzı tasarım sabitleri.

## Temel Kütüphaneler
- **Axios:** API haberleşmesi.
- **React Navigation:** Ekranlar arası geçiş.
- **Native WebSocket** (`frontend/services/SocketService.js`, `new WebSocket(...)`): Multiplayer mod için canlı soket bağlantısı — socket.io-client değil, tarayıcı/React Native'in yerleşik `WebSocket` API'si kullanılır; backend tarafında da (`routers/multiplayer.py`) FastAPI'nin native `WebSocket` desteği kullanılır, socket.io protokolü değil.
- **Expo Blur:** Oyun içi "Glassmorphism" ve modern bulanık tasarım efektleri için.
