# Getting Started

Football TicTacToe projesi hem bir backend sunucusundan (FastAPI) hem de bir mobil uygulamadan (React Native / Expo) oluşur.

## 1. Backend Kurulumu

Backend klasörüne gidin ve sanal ortamı aktif edin:
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows için
# source venv/bin/activate # Linux/Mac için
```

Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

`.env` dosyanı oluştur (bkz. `.env.example`) ve `DATABASE_URL_V2` değişkenini doldur — bu değişken olmadan `database.py` uygulamayı başlatmaz:
```bash
cp .env.example .env
# .env icini ac ve DATABASE_URL_V2'yi doldur (yerel SQLite icin sqlite:///./football_trivia.db yeterli)
```

Veritabanını başlatın (Eğer `.db` dosyası yoksa, yalnızca yerel SQLite ile çalışıyorsan gerekir):
```bash
python init_db.py
```

FastAPI sunucusunu başlatın:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Artık backend `http://localhost:8000` adresinde çalışmaktadır.

## 2. Frontend (React Native) Kurulumu

Yeni bir terminal açın ve `frontend` klasörüne gidin:
```bash
cd frontend
npm install
```

Projeyi başlatın:
```bash
npx expo start
```
Açılan menüden **a** tuşuna basarak Android emülatöründe veya Expo Go uygulaması ile kendi cihazınızda çalıştırabilirsiniz.

::: tip
Geliştirme aşamasında lokal cihazınız ile emülatörün aynı ağda olduğuna dikkat edin. API URL ayarlarınızı `api.js` içerisinden yapılandırabilirsiniz.
:::
