# Bayraklarla Kurulu İlk 11 Modu — "Bayrak XI"

Görsel hafıza ve coğrafya bilgisinin futbolla harmanlandığı, oyunculara sadece "uyruklar" üzerinden ipucu verilen bir moddur.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir.
:::

## Kadro Seçimi (kesin algoritma — mevcut şemayla çalışır)
`models.py`'de "belirli bir maçın ilk 11'i" bilgisini tutan bir tablo **yoktur** (`player_club_stats` yalnızca sezon bazlı toplam istatistik tutar, maç bazlı kadro değil). Yeni bir veri toplama süreci gerektirmemek için kadro şöyle **hesaplanır**: rastgele bir takım + sezon (`player_club_stats.team_id` + `season`) seçilir, o takım-sezon kombinasyonunda **en çok `appearances`'a sahip 11 oyuncu** o sezonun "temsili İlk 11"i olarak kabul edilir. Bu, gerçek bir maçın kadrosu değil ama o sezonun en çok oynayan kadrosudur — kasıtlı ve yeterli bir yaklaşımdır.

- Yalnızca en az 11 farklı oyuncusu **appearances > 5** olan takım-sezon kombinasyonları aday havuzuna girer (çok küçük/eksik veri kümelerini elemek için).
- Kadronun mevkilere (`players.position`: Goalkeeper/Defender/Midfield/Attack) dağılımı 4-3-3 kalıbına **zorlanmaz** — gerçek appearances sıralamasına göre çıkan doğal dağılım (örn. 1 Kaleci + 4 Defans + 4 Ortasaha + 2 Forvet) olduğu gibi kullanılır, çünkü hedef gerçekçi bir kadro göstermektir, yapay bir diziliş değil.

## Oyun Mantığı
- Ekranda bir futbol sahası belirir; 11 oyuncunun mevkilerine (`position` alanına göre kabaca yerleştirilmiş) **isim yerine uyruk bayrağı** (`nationality`) konur.
- Kullanıcı sadece bayraklara bakarak kadronun **hangi takım + hangi sezon** olduğunu tahmin etmeye çalışır. **Tahmin biçimi kesin olarak takım adıdır** (bireysel oyuncu tahmini yoktur — bu, modu basit ve hızlı tutar).

## Kurallar
- **Offline Mod:** Kullanıcının takımı bulmak için toplam **3 hakkı** vardır. Yanlış tahminde sistem bir ipucu açar: 1. yanlıştan sonra takımın ülkesi, 2. yanlıştan sonra sezon (yıl) gösterilir.
- **Online Mod:** İki oyuncu aynı sahayı görür, [Find Player From Two](/guide/game-modes/find-player-from-two) ile aynı buzzer deseninde **ilk doğru tahmini yapan** kazanır; her iki tarafın da maksimum **3 tahmin hakkı** vardır (hakkı biten oyuncu o el için tahmin yapamaz ama rakip hâlâ deniyorsa el devam eder). **30 saniye** süre sınırı vardır; süre dolduğunda veya iki taraf da hakkını tüketince el berabere biter, oda ücreti iade edilir.

## Kısıtlamalar ve Uç Durumlar
- **Aynı uyruktan birden çok oyuncu:** Kadronun 11 oyuncusundan **6 veya fazlası aynı uyruktaysa** (örn. bir Türk kulübünün büyük çoğunluğu yabancıysa bu durum nadir ama olası), bu kadro-sezon kombinasyonu "Zor" olarak etiketlenir ve seçim havuzunda daha düşük ağırlıkla yer alır (tamamen elenmez, sadece `random.choices` ağırlığı 3'te 1'e düşürülür) — ipucu zayıflığını dengeler.
- **Çift uyruklu oyuncular:** `players.nationality` alanı tek bir değer tutar (scraper'ın Transfermarkt'tan çektiği birincil/fiilen temsil edilen uyruk) — ek bir karar mekanizmasına gerek yoktur, alan zaten tekil.
- **Takım adı eşleşmesi:** Kullanıcının yazdığı isim `teams.short_name`/`teams.name` üzerinde [TicTacToe arama](/guide/game-modes/tictactoe-4x4)'daki fuzzy-arama mantığıyla değerlendirilir; sezonu belirtmesi gerekmez, yalnızca doğru takımı bilmesi yeterlidir.

## Backend İhtiyaçları (uygulanacak API sözleşmesi)
- `GET /api/game/flag-eleven/generate` → yukarıdaki algoritmayla bir takım-sezon seçer, yanıt: `{"puzzle_id": "...", "positions": [{"slot": "GK", "nationality": "Brazil"}, ...11 slot], "team_id": 123}` (takım adı/sezonu **cevap olduğu için** yanıtta döndürülmez, yalnızca `verify` ile kontrol edilir).
- `POST /api/game/flag-eleven/verify` → `{"puzzle_id": "...", "team_guess": "Real Madrid"}`; `teams.short_name`/`name` ile fuzzy eşleştirip doğru/yanlış döner.
