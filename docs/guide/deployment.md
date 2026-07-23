# Deployment & Canlıya Alma

Projenin tam anlamıyla dış dünyaya açılması için gerekli adımlar.

## Backend Deployment (VPS / Ubuntu)
1. Sunucunuza Python 3.10+ kurun.
2. Nginx ayarlarında Reverse Proxy tanımlayarak gelen 80/443 isteklerini lokaldeki 8000 portuna yönlendirin.
3. **Gunicorn & Uvicorn** kullanarak FastAPI'yi asenkron worker'larla çalıştırın:
```bash
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --workers 4
```
4. PM2 veya Systemd ile servisi arka planda kalıcı hale getirin.
5. `DATABASE_URL_V2` ortam değişkenini (production Postgres bağlantı dizesi) sunucu/deploy platformunun kendi ortam değişkeni deposunda tanımlayın — `backend/database.py` bu değişken olmadan başlamayı reddeder. **Bu değeri asla koda veya git'e commit etmeyin**, sadece `.env` (gitignore'da) veya platformun secret yönetiminde tutun.

::: warning Bu bölüm doğrulanmadı
Gerçek deploy platformunuz (VPS mi, bir PaaS mi) bu oturumda teyit edilmedi — yukarıdaki adımlar genel bir varsayım. Gerçek kurulumunuzu söylerseniz bu sayfayı buna göre güncelleyebiliriz.
:::

## Frontend (Expo) Deployment
React Native uygulamasını marketlere göndermek (veya test etmek) için Expo EAS kullanılır.
```bash
npm install -g eas-cli
eas login
eas build -p android --profile preview
```
Bu komut size direkt kurabileceğiniz bir APK (veya AAB) dosyası sunar. iOS için `-p ios` ile IPA build alınabilir (Apple Developer hesabı gerektirir).
