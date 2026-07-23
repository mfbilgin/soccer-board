# Veritabanı Mimarisi

Tabloların ne tuttuğu için [Database Structure](/guide/database) sayfasına bakın. Burası şemanın **nasıl yönetildiğine** (migrasyon yerine ne kullanıldığına) ve tasarım prensiplerine odaklanır.

## Klasör Yapısı

```
backend/
├── models.py                        # Tek şema kaynağı (SQLAlchemy Base)
├── database.py                       # engine + SessionLocal (DATABASE_URL_V2 okur)
├── data/countries.csv                 # country_id → country_name statik referans verisi
└── scripts/
    ├── add_height_cm_column.py        # Idempotent ALTER TABLE örneği
    ├── backfill_team_profiles.py       # Bozuk/eksik takım verisini TMAPI'den onarır
    ├── backfill_player_heights.py      # height_cm IS NULL olanları doldurur
    └── clean_team_names.py             # short_name IS NULL olanları düzenler (fill-only)
```

`scraper_bot/models_v2.py`, `backend/models.py` ile **aynı tabloları** ayrı bir `Base` üzerinden tanımlayan bağımsız bir dosyadır — bkz. [Genel Bakış / Bilinen Sınırlamalar](/architecture/overview).

## Katmanlar

1. **ORM modeli (`models.py`)** — şemanın tanımlandığı tek yer. Yeni bir kolon/tablo önce burada tanımlanır.
2. **Şema oluşturma (`Base.metadata.create_all`)** — yalnızca `main.py` başlarken çağrılır ve yalnızca **eksik tabloları** oluşturur; var olan bir tabloya yeni kolon eklemez (bkz. Tasarım Prensipleri).
3. **Idempotent bakım script'leri (`scripts/`)** — `models.py`'de tanımlanan ama üretimdeki tabloda henüz var olmayan bir kolonu eklemek veya var olan bozuk veriyi onarmak için elle çalıştırılır.
4. **Veri hattı (scraper → Postgres)** — `scraper_bot/distributed_scraper.py`, aynı `DATABASE_URL_V2`'ye (farklı bir ortamdan/makineden bile olsa) yazar; detaylar için [Scraper Infrastructure](/guide/scraper-api).

## Tasarım Prensipleri

- **Migrasyon çerçevesi yok (Alembic kullanılmıyor).** `Base.metadata.create_all(bind=engine)` SQLAlchemy'nin **yalnızca eksik tabloları** oluşturduğu, var olan bir tabloya kolon eklemediği bilinerek kullanılıyor. Bir modele yeni bir kolon eklendiğinde (`models.py`), production'daki tabloya bunun yansıması için elle bir `ALTER TABLE ... ADD COLUMN IF NOT EXISTS ...` script'i yazılıp bir kere çalıştırılmalıdır — bkz. `scripts/add_height_cm_column.py` (bu session'da `players.height_cm` eklenirken kullanılan kanonik örnek).
- **Backfill script'leri her zaman "hâlâ bozuk olanı hedefle" şeklinde yazılır.** `WHERE height_cm IS NULL` / `WHERE name ~ '^Team \d+$' OR country IS NULL` gibi bir koşulla çalışan script'ler, yarıda kesilse bile güvenle tekrar çalıştırılabilir — zaten düzeltilmiş satırları asla yeniden işlemezler. Yeni bir backfill yazarken bu koşullu-sorgu deseni zorunlu kabul edilir.
- **`--limit N` ile küçük parti testi.** Her backfill script'i, production'a tam çalıştırmadan önce küçük bir örneklemle (`--limit 20` gibi) doğrulanabilecek şekilde yazılır.
- **Tek gerçek kaynak: production Postgres.** Yerel geliştirme SQLite ile yapılabilir ama hangi script'in hangi veritabanına yazdığı her zaman `.env`'deki `DATABASE_URL_V2`'den kontrol edilir; iki ortam aynı anda karıştırılmaz.
- **Genel amaçlı "override" listeleri yerine otoriter kaynağa güven.** Takım kısa isimlerini düzeltmek için elle tutulan bir `ELITE_CLUB_OVERRIDES` listesi (geniş `LIKE` desenleriyle) önceden kullanılıyordu; bu, alakasız kulüpleri (örn. "Arsenal Tula") yanlışlıkla aynı isme indirgeyebildiği için kaldırıldı. Artık Transfermarkt'ın TMAPI'sindeki resmi `shortName`/`countryId` alanları otoriter kaynak kabul ediliyor; elle tutulan bir liste yerine dış API'den gelen veri tercih ediliyor.

## Bilinen Sınırlamalar

- `scraper_bot/models_v2.py` ile `backend/models.py` senkron tutulmalıdır; birine kolon eklenip diğeri unutulursa (örn. yalnızca backend'e `height_cm` eklenip scraper'a eklenmezse) scraper o alanı hiç yazmaz, sessizce eksik kalır.
- `player_honours` tablosu şemada tanımlı ama hiç veri girilmemiş, boş bir tablo.
- `players.height_cm` backfill'i tamamlanana kadar Extreme Squad modunun `tallest` kriteri yeterli takım kapsaması bulamayabilir ve otomatik olarak `youngest`'e düşer (bkz. [current-task.md](/current-task)).
