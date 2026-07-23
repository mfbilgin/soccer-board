# Bayraklarla Kurulu İlk 11 Modu — "Bayrak XI"

Görsel hafıza ve coğrafya bilgisinin futbolla harmanlandığı, oyunculara sadece "uyruklar" üzerinden ipucu verilen bir moddur.

**Durum:** Kodlandı ve çalışıyor (hem singleplayer hem online).

Kod karşılığı: `backend/routers/flag_eleven.py` (`generate_puzzle`, `/generate`, `/verify` — cevabı sunucu tarafında `PUZZLES` bellek önbelleğinde tutar, yanıtta asla döndürmez), `backend/routers/multiplayer.py`'deki `flag_eleven_timer`/`finish_flag_eleven` (online: tek el, mevcut tier kuyruğu üzerinden `game_mode: "flag_eleven"`), `frontend/screens/singleplayer/FlagElevenScreen.js`, `frontend/screens/multiplayer/MultiplayerFlagElevenScreen.js`.

## Kadro Seçimi
Veri modelinde "belirli bir maçın ilk 11'i" bilgisini tutan bir tablo yoktur (mevcut istatistik tabloları yalnızca sezon bazlı toplam tutar, maç bazlı kadro değil). Bu nedenle kadro şöyle hesaplanır: rastgele bir takım + sezon seçilir, o takım-sezon kombinasyonunda **en çok maça çıkan 11 oyuncu** o sezonun "temsili İlk 11"i olarak kabul edilir. Bu, gerçek bir maçın kadrosu değil ama o sezonun en çok oynayan kadrosudur.

- Yalnızca en az 11 farklı oyuncusu 5'ten fazla maça çıkmış takım-sezon kombinasyonları aday havuzuna girer (çok küçük/eksik veri kümelerini elemek için).
- Kadronun mevkilere dağılımı 4-3-3 kalıbına zorlanmaz — gerçek maç sayısı sıralamasına göre çıkan doğal dağılım (örn. 1 Kaleci + 4 Defans + 4 Ortasaha + 2 Forvet) olduğu gibi kullanılır, çünkü hedef gerçekçi bir kadro göstermektir, yapay bir diziliş değil.

## Oyun Mantığı
- Ekranda bir futbol sahası belirir; 11 oyuncunun mevkilerine (kabaca yerleştirilmiş) isim yerine **uyruk bayrağı** konur.
- Kullanıcı sadece bayraklara bakarak kadronun hangi takım + hangi sezon olduğunu tahmin etmeye çalışır. Tahmin biçimi **takım adıdır** (bireysel oyuncu tahmini yoktur — bu, modu basit ve hızlı tutar).

## Kurallar
- **Offline Mod:** Kullanıcının takımı bulmak için toplam **3 hakkı** vardır. Yanlış tahminde sistem bir ipucu açar: 1. yanlıştan sonra takımın ülkesi, 2. yanlıştan sonra sezon (yıl) gösterilir.
- **Online Mod:** İki oyuncu aynı sahayı görür, [Find Player From Two](/guide/game-modes/find-player-from-two) ile aynı buzzer deseninde **ilk doğru tahmini yapan** kazanır; her iki tarafın da maksimum **3 tahmin hakkı** vardır (hakkı biten oyuncu o el için tahmin yapamaz ama rakip hâlâ deniyorsa el devam eder). **30 saniye** süre sınırı vardır; süre dolduğunda veya iki taraf da hakkını tüketince el berabere biter, oda ücreti iade edilir.

## Kısıtlamalar ve Uç Durumlar
- **Aynı uyruktan birden çok oyuncu:** Kadronun 11 oyuncusundan 6 veya fazlası aynı uyruktaysa, bu kadro-sezon kombinasyonu "Zor" olarak etiketlenir ve seçim havuzunda daha düşük ağırlıkla yer alır (tamamen elenmez, ağırlığı 3'te 1'e düşürülür).
- **Çift uyruklu oyuncular:** Veri modelinde tekil bir uyruk alanı tutulur (fiilen temsil edilen milli takım) — ek bir karar mekanizmasına gerek yoktur.
- **Takım adı eşleşmesi:** Kullanıcının yazdığı isim [TicTacToe arama](/guide/game-modes/tictactoe-4x4)'daki fuzzy-arama mantığıyla değerlendirilir; sezonu belirtmesi gerekmez, yalnızca doğru takımı bilmesi yeterlidir.

## Backend Sözleşmesi
- `GET /api/game/flag-eleven/generate` → yukarıdaki algoritmayla bir takım-sezon seçer, yanıt: `{"puzzle_id": "...", "positions": [{"slot": "GK", "nationality": "Brazil"}, ...11 slot], "team_id": 123}` (takım adı/sezonu cevap olduğu için yanıtta döndürülmez, yalnızca doğrulama ile kontrol edilir).
- `POST /api/game/flag-eleven/verify` → `{"puzzle_id": "...", "team_guess": "Real Madrid"}`; takım adıyla fuzzy eşleştirip doğru/yanlış döner.
