# Kimlik Doğrulama Ekranları (Auth Screens)

Kullanıcıların uygulamaya giriş yaptığı, kayıt olduğu ve güvenlik jetonlarını (JWT Token) aldıkları ekranlardır.

## LoginScreen.js
Kullanıcıların mevcut hesaplarına giriş yaptığı ilk karşılama ekranıdır.
- **Kullanıcı Akışı:** Kullanıcı adı ve şifre girilir.
- **Arka Plan İşlemi:** Form verileri FastAPI backend'indeki `/token` endpoint'ine gönderilir. Başarılı olursa dönen JWT Token, telefonun yerel depolama belleğine (`AsyncStorage` / `SecureStore`) kaydedilir.
- **Tasarım:** Modern, futbolu andıran dinamik bir arka plan, bulanıklaştırılmış (glassmorphism) giriş formu.

## RegisterScreen.js
Yeni oyuncuların sisteme dahil olduğu ekrandır.
- **Kullanıcı Akışı:** E-posta, kullanıcı adı ve güvenli şifre istenir. Şifrelerin eşleşip eşleşmediği arayüzde kontrol edilir.
- **Hata Yönetimi:** "Bu kullanıcı adı zaten alınmış" gibi backend'den gelen 400 Bad Request hataları, ekranda zarif uyarılar (Toasts) ile kullanıcıya gösterilir.
