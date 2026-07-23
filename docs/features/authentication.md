# Özellik: Kimlik Doğrulama

**Durum:** Kodlandı ve çalışıyor.

Mimari/tercih gerekçesi için [ADR 001](/decisions/001-auth) sayfasına bakın. Bu sayfa özelliğin kullanıcı/API açısından ne yaptığını anlatır.

## Akış

1. **Kayıt** — `POST /api/auth/register` (`username`, `email`, `password`). Kullanıcı adı veya e-posta zaten kayıtlıysa `400` döner. Yeni kullanıcı 1000 chip, 20 gem, 100 rating, 1. seviye ile başlar.
2. **Giriş** — `POST /api/auth/login` (OAuth2 password flow: `form_data.username`/`form_data.password`). Başarılıysa 30 gün geçerli bir JWT (`access_token`) döner.
3. **Profil okuma** — `GET /api/auth/me` (Bearer token gerektirir) — güncel `xp`, `level`, `chips`, `gems`, `rating` dahil kullanıcı bilgisini döner. Uygulama genelinde "kullanıcının şu anki durumu" bu endpoint'ten okunur (bkz. [ADR 002](/decisions/002-state-management) — küresel bir profil state'i olmadığı için bu endpoint çok sık, bağımsız ekranlardan çağrılır).
4. **İstemci tarafı** — Token `expo-secure-store`'a yazılır; sonraki tüm REST isteklerine axios interceptor'ı otomatik ekler; WebSocket bağlantısı da aynı token'ı `?token=...` query param'ıyla gönderir.

## Kısıtlamalar ve Uç Durumlar

- Kullanıcı adı/e-posta benzersizliği veritabanı seviyesinde (`unique=True`) ve endpoint seviyesinde (açık kontrol) olmak üzere iki kez garanti edilir.
- Yanlış kullanıcı adı/şifre, sızıntıyı önlemek için aynı `401 Incorrect username or password` mesajını döner (hangisinin yanlış olduğu ayrıştırılmaz).
- **Bilinen istemci hatası:** `LoginScreen.js`, ağ hatası/timeout ile gerçekten yanlış şifreyi aynı jenerik "Giriş başarısız. Bilgilerinizi kontrol edin." mesajıyla gösterir — kullanıcı bağlantı sorunu yaşarken "şifremi mi unuttum" diye düşünebilir. Düzeltilmedi, bkz. [current-task.md](/current-task).
- Şifre sıfırlama (forgot password) akışı yok — kullanıcı şifresini unutursa şu an geri kazanma yolu yok.
