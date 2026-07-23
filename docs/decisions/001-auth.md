# ADR 001 — Kimlik Doğrulama: JWT + bcrypt

**Durum:** Kabul edildi, uygulandı (`backend/security.py`, `backend/routers/auth.py`).

## Bağlam

Mobil bir oyun için kullanıcı kaydı/girişi gerekiyordu. Gereksinimler:
- Her istekte (REST **ve** WebSocket) kullanıcıyı doğrulayabilmek.
- Kullanıcının sık sık yeniden giriş yapmasını istemeyen, oyun-dostu bir oturum süresi.
- Şifreleri düz metin veya geri döndürülebilir şekilde saklamamak.

## Karar

- **Şifre hash'leme:** `passlib`'in `bcrypt` şeması (`security.py`'deki `pwd_context`).
- **Oturum:** Durum tutmayan (stateless) JWT — `python-jose` ile `HS256` imzalı, `{"username": ..., "exp": ...}` payload'ı.
- **Token ömrü:** 30 gün (`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30`) — bilinçli olarak uzun tutuldu; yorum satırında da belirtildiği gibi "oyunlar için uzun token süresi iyidir" (kullanıcıyı ayda bir defadan fazla yeniden login'e zorlamamak için).
- **İstemci tarafı saklama:** Token, `expo-secure-store` ile cihazın güvenli deposunda tutulur; `frontend/api.js`'teki axios `request` interceptor'ı her isteğe otomatik `Authorization: Bearer <token>` ekler.
- **WebSocket kimlik doğrulama:** Aynı JWT, bağlantı URL'sine query param olarak eklenir (`?token=...`) ve `routers/multiplayer.py`'deki `get_current_user_ws` ile REST'teki `get_current_user`'a paralel şekilde doğrulanır — WebSocket handshake'inde `Authorization` header'ı kullanılamadığı için bu yol seçildi.
- **Varsayılan yeni kullanıcı durumu:** 1000 chip, 20 gem, 100 rating (`models.User` kolon varsayılanları) — bkz. [Gems & Chips](/guide/systems/economy-gems-chips).

## Sonuçlar

- ✅ Basit, framework'ün (`fastapi.security.OAuth2PasswordBearer`) doğrudan desteklediği bir akış; hem REST hem WS aynı token'ı doğrular.
- ⚠️ **`SECRET_KEY` şu an `security.py` içinde düz metin olarak hardcoded** (`"football-trivia-super-secret-key-do-not-share"`), kod içinde de "gerçek bir projede .env dosyasından okunmalıdır" notu var. Bu, repo'ya erişimi olan herkesin sıfırdan geçerli bir token üretebileceği anlamına gelir — production'a geçmeden önce ortam değişkenine taşınmalı.
- ⚠️ 30 günlük token'ın iptal (revoke) mekanizması yok — bir token çalınırsa süresi dolana kadar geçerlidir. Kabul edilen bir risk (oyun uygulaması, bankacılık değil), ama bilinmesi gereken bir ödünleşim.
- Token yenileme (refresh token) akışı yok; süre dolduğunda kullanıcı yeniden `/api/auth/login` yapmalıdır.
