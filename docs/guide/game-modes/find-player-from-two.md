# 2 Takım/Ülkeden Futbolcu Bul Modu — "Kesişim Düellosu"

Yalnızca online oynanabilen, yüksek hız ve bilgi gerektiren spesifik bir refleks (buzzer) modudur.

**Durum:** Kodlandı ve çalışıyor.

Kod karşılığı: `backend/find_two.py` (`FindTwoEngine` — kriter üretimi ve doğrulama, `tictactoe.py`'nin takım/oyuncu önbelleğini yeniden kullanır), `backend/routers/multiplayer.py`'deki `find_two_timer`/`find_two_next_round`/`finish_find_two` (mevcut tier kuyruğu üzerinden `game_mode: "find_two"`), `frontend/screens/multiplayer/FindTwoScreen.js`.

## Modun Türleri
Oyun, oda kurulurken rastgele seçilen iki türden birinde oynanır:

### 1. Takım & Ülke Modu
- Sistem bir tarafta bir **Kulüp Takımı**, diğer tarafta bir **Ülke (Milli Takım)** gösterir.
- *Örnek:* Real Madrid & Hırvatistan.
- *Amaç:* Kariyerinde Real Madrid forması giymiş, Hırvat uyruklu bir oyuncuyu (Örn: Luka Modric) **ilk yazan** oyuncu turu kazanır.

### 2. Takım & Takım Modu
- Sistem iki farklı **Kulüp Takımı** gösterir.
- *Örnek:* Juventus & Manchester United.
- *Amaç:* Her iki takımda da forma giymiş bir oyuncuyu (Örn: Paul Pogba) ilk yazan taraf turu kazanır.

## Kriter Üretimi ve Çözülebilirlik Garantisi
Kriter üretimi, [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki ızgara üretim algoritmasının kullandığı takım→oyuncu ve oyuncu→takım önbelleğini yeniden kullanır:

- **Takım & Takım:** Popüler takımlar havuzundan rastgele bir takım A seçilir; A ile ortak oyuncusu olan (kesişen), A'dan farklı bir takım B, yine popüler takımlar havuzundan seçilir.
- **Takım & Ülke:** Rastgele bir kulüp takımı A seçilir; A'da oynamış oyunculardan rastgele birinin uyruğu okunur ve "ülke" kriteri olarak o uyruk kullanılır — bu, A ile kesişimin garanti olduğu bir ülke seçilmesini sağlar.

Bu yöntemle kriterler zaten kesişimi garanti eden bir sorgudan üretildiği için ayrı bir "çözülebilirlik kontrolü" adımına gerek kalmaz.

## Akış (Online, gerçek zamanlı, buzzer usulü)
1. Oda kurulur, kriterler üretilip her iki oyuncuya da aynı anda yayınlanır.
2. Her iki oyuncu da aynı anda, sıra beklemeden tahmin gönderebilir (WebSocket `action: "find_two_guess", entity_id: <player_id>`).
3. Sunucu gelen her tahmini anında doğrular: oyuncunun kariyer verilerinde hem A hem B (veya A hem ülke) ile eşleşme var mı kontrol edilir.
4. **İlk geçerli/doğru cevabı gönderen** turu kazanır — sunucu, aynı anda gelen istekleri sunucuya ulaşma sırasına göre değerlendirir; ikinci gelen istek "tur bitti" durumunda reddedilir.
5. **Süre Sınırı:** 30 saniye içinde kimse doğru cevap veremezse tur berabere biter, oda ücreti iade edilir.
6. **Yanlış tahmin cezası:** Yanlış tahmin gönderen oyuncu 3 saniye boyunca yeni tahmin gönderemez (rastgele isim sallamayı/spam'i engellemek için).
7. **Maç formatı:** Tek bir kriter turu değil, **ilk 3 turu kazanan** (best-of-5) maçı kazanır. Her tur biter bitmez yeni bir kriter çifti üretilip bir sonraki tura geçilir.

## Backend Sözleşmesi
- Multiplayer oda başlatma akışına `game_mode: "find_two"` dalı: kriter üretimi + `room.game_state = {"criteria": {...}, "score": {p1: 0, p2: 0}, "round": 1}`.
- WebSocket action `find_two_guess`: gelen `entity_id`'nin kariyer verilerinde her iki kritere de uyup uymadığını kontrol eden, doğruysa skoru artırıp ya yeni turu başlatan ya da (skor 3'e ulaştıysa) maçı kapatan bir handler.

## Kısıtlamalar ve Uç Durumlar
- **Çoklu doğru cevap:** Kriterlere uyan birden fazla oyuncu olabilir; hangisi olursa olsun ilk geçerli cevap yeterlidir, "tek doğru cevap" diye bir kısıt yoktur.
- **Eşzamanlı doğru cevaplar:** Sunucu, WebSocket mesajlarını sıraya aldığı için "aynı anda" gelen iki doğru cevap bile aslında sunucuda milisaniyeler farkla işlenir — ilk işlenen kazanır, ikinci oyuncuya "rakip daha hızlıydı" mesajı gösterilir.
