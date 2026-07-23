# 2 Takım/Ülkeden Futbolcu Bul Modu — "Kesişim Düellosu"

Yalnızca online oynanabilen, yüksek hız ve bilgi gerektiren spesifik bir refleks (buzzer) modudur.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir.
:::

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

## Kriter Üretimi ve Çözülebilirlik Garantisi (kesin algoritma)
Backend, sunucu açılışında kurulan `TicTacToeEngine` önbelleğindeki `team_players` (takım → oyuncu kümesi) ve `player_teams` (oyuncu → takım kümesi) yapılarını **yeniden kullanır** (ayrı bir önbellek kurmaya gerek yoktur):

- **Takım & Takım:** `popular_team_ids` havuzundan rastgele bir takım A seçilir; `team_players[A]` kümesindeki oyunculardan en az birinin oynadığı, A'dan farklı bir takım B, yine `popular_team_ids` içinden seçilir (yani A ile B'nin `team_players` kümeleri kesişmelidir). Bu, [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki ızgara üretim algoritmasıyla birebir aynı kesişim mantığıdır.
- **Takım & Ülke:** Rastgele bir kulüp takımı A (`popular_team_ids`'den) seçilir; `team_players[A]`'daki oyunculardan rastgele birinin `nationality` alanı okunur ve "ülke" kriteri olarak o uyruk kullanılır — bu, A ile kesişimin **garanti olduğu** bir ülke seçilmesini sağlar (çünkü doğrudan A'da oynamış gerçek bir oyuncudan türetilir).

Bu yöntemle **ekstra bir "çözülebilirlik kontrolü" adımına gerek kalmaz** — kriterler zaten kesişimi garanti eden bir sorgudan üretilir.

## Akış (Online, gerçek zamanlı, buzzer usulü)
1. Oda kurulur, backend yukarıdaki algoritmayla kriterleri üretir ve `criteria_ready` mesajıyla her iki oyuncuya da aynı anda yayınlar.
2. Her iki oyuncu da **aynı anda**, sıra beklemeden tahmin gönderebilir (WebSocket `action: "find_two_guess", entity_id: <player_id>`).
3. Backend gelen her tahmini **anında** doğrular: oyuncunun `player_club_stats`/`player_national_stats` kayıtlarında hem A hem B (veya A hem ülke) ile eşleşme var mı kontrol edilir.
4. **İlk geçerli/doğru cevabı gönderen** turu kazanır — backend, aynı anda gelen istekleri **sunucuya ulaşma sırasına (timestamp)** göre değerlendirir; ikinci gelen istek zaten "tur bitti" durumunda reddedilir.
5. **Süre Sınırı:** **30 saniye** içinde kimse doğru cevap veremezse tur **berabere** biter, oda ücreti iade edilir (rake alınmaz).
6. **Yanlış tahmin cezası:** Yanlış tahmin gönderen oyuncu **3 saniye boyunca** yeni tahmin gönderemez (rastgele isim sallamayı/spam'i engellemek için sunucu tarafında bir "cooldown" uygulanır); doğru tahmin eden taraf varsa bu cooldown'dan etkilenmeden oyun zaten biter.
7. **Maç formatı:** Tek bir kriter turu değil, **ilk 3 turu kazanan** (best-of-5) maçı kazanır — [TicTacToe](/guide/game-modes/tictactoe-4x4) ve [Stats Target](/guide/game-modes/stats-target)'ın aksine bu mod tek turluk değil, çünkü tek bir buzzer turu çok kısa sürdüğünden tek turla eşleşme hissi zayıf kalır. Her tur biter bitmez yeni bir kriter çifti üretilip bir sonraki tura geçilir.

## Backend İhtiyaçları (uygulanacak API/WebSocket sözleşmesi)
- `multiplayer.py`'de yeni bir `game_mode: "find_two"` dalı: `initialize_game_state` içinde kriter üretimi + `room.game_state = {"criteria": {...}, "score": {p1: 0, p2: 0}, "round": 1}`.
- WebSocket action `find_two_guess`: gelen `entity_id`'nin `player_club_stats`/`player_national_stats` üzerinden her iki kritere de uyup uymadığını kontrol eden, doğruysa `score[user_id] += 1` yapıp ya yeni turu başlatan ya da (skor 3'e ulaştıysa) `award_winnings` + `update_rating` çağırıp odayı kapatan bir handler.

## Kısıtlamalar ve Uç Durumlar
- **Çoklu doğru cevap:** Kriterlere uyan birden fazla oyuncu olabilir; hangisi olursa olsun ilk geçerli cevap yeterlidir, "tek doğru cevap" diye bir kısıt yoktur.
- **Eşzamanlı doğru cevaplar:** Sunucu, WebSocket mesajlarını sıraya aldığı için "aynı anda" gelen iki doğru cevap bile aslında sunucuda milisaniyeler farkla işlenir — ilk işlenen kazanır, ikinci oyuncuya "rakip daha hızlıydı" mesajı gösterilir.
