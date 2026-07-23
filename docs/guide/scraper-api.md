# Scraper ve Veri Güncelleme (Scraper API)

Uygulamanın kalbi, güncel futbol istatistiklerinin çekildiği **Transfermarkt API (TMAPI)** ve **CEAPI** altyapısına dayanır. Scraper kodu `scraper_bot/` dizininde yaşar (`backend/`'de artık kopyası yok — tek gerçek kaynak burasıdır).

::: warning Hangi veritabanına yazıyor?
`scraper_bot/database_v2.py`, `DATABASE_URL_V2` ortam değişkenini okur ve set edilmemişse **yerel** bir sqlite dosyasına (`football_trivia_v2.db`) düşer — bu güvenli bir "dry run" davranışıdır. Production Postgres'e yazmak için bu değişkeni `backend/.env.example`'daki prod bağlantı formatına set etmen gerekir. Yanlışlıkla local mi prod'a mı yazdığını her çalıştırmadan önce kontrol et.
:::

## TMAPI (performance-game)
Kulüp ve milli takım istatistikleri için kullanılan asıl endpoint, bir oyuncunun tüm kariyer maçlarını tek seferde dönen `performance-game` uç noktasıdır:
`https://tmapi.transfermarkt.technology/player/{id}/performance-game`

Bu endpoint bize oyuncunun:
- Sahada kalma süresini (`participationState`, `playedMinutes`)
- Gol, asist ve penaltı istatistiklerini
- Sarı/kırmızı kartlarını
- Oynadığı turnuvaları (`competitionId`) liste olarak verir.

**Güvenlik filtreleri:** Sadece `participationState == 'played'` olan maçlar sayılır (yedek kalınan/sakatlık maçları hariç); `competitionId == 'FS'` olan hazırlık maçları resmi istatistik kabul edilmez.

## CEAPI (transferHistory)
Transfer geçmişi ayrı bir uç noktadan, `transferHistory/list/{id}` üzerinden çekilir (`https://www.transfermarkt.com.tr/ceapi/...`). Oyuncunun `to`/`from` takımları, tarih ve bedel bilgisi buradan gelir. Emeklilik tespiti de bu akışta yapılır: oyuncu `123` (Emekli/Retired) ID'li "takıma" transfer olmuşsa `is_active = False` işaretlenir.

## distributed_scraper.py (Ana Scraper)
`scraper_bot/distributed_scraper.py`, veritabanında **zaten var olan** oyuncu kayıtlarını (`Player.id`) belirli bir aralıkta (`--start`, `--end`) tarayıp TMAPI + CEAPI'den güncel istatistik/transfer verisini çeker ve `player_club_stats`, `player_national_stats`, `player_transfers` tablolarına upsert eder. "Distributed" adı, farklı ID aralıklarının paralel/farklı makinelerde çalıştırılabilmesinden gelir:

```bash
cd scraper_bot
python distributed_scraper.py --start 1 --end 16000
```

Takım ve turnuva kayıtları (`teams`, `competitions`) scraping sırasında ilk karşılaşıldığında otomatik oluşturulur (`get_or_create_team`, `get_or_create_competition`).

::: info Oyuncu keşfi kapsam dışı
`distributed_scraper.py` yeni oyuncu **keşfetmez** — sadece DB'de zaten var olan `Player` satırlarını günceller. İlk oyuncu/takım listesinin nereden geldiği (`backend/src/` altındaki `01_fetch_players_by_league.py`, `extract_player_ids.py` gibi script'ler veya Kaggle veri seti importu) ayrı bir adımdır ve bu doküman kapsamı dışındadır.
:::

## Takım İsimlerini Temizleme
Transfermarkt'tan gelen takım isimleri genelde uzun kurumsal formdadır ("Futbol Club Barcelona S.A.D." gibi). `backend/scripts/clean_team_names.py`, bunları regex ile temizleyip `teams.short_name` alanına yazar; popüler kulüpler için elle belirlenmiş kısa isimleri (Beşiktaş, PSG, Real Madrid vb.) üzerine uygular. İdempotenttir, tekrar tekrar çalıştırılabilir.
