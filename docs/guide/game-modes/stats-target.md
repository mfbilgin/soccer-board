# İstatistik Hedefleri Modu (Stats Target / "Kariyer İstatistiği Avı")

Kullanıcının, sistemin verdiği sabit sayıda futbolcuyla, belirli bir kapsamda (lig veya milli takım) verilen bir istatistik hedefine **olabildiğince yakınlaşmaya** çalıştığı bir moddur. **Amaç hedefi aşmak değil, hedefe tam olarak (ya da olabildiğince yakın) ulaşmaktır.**

::: tip Düzeltildi
Daha önce burada, online modun `routers.mode_3_1` adlı artık var olmayan bir modülü import ettiği için çöktüğü belirtiliyordu. Bu düzeltildi: `multiplayer.py` artık `routers/target_score.py`'yi import ediyor; ayrıca `validate_submission`'ın saf hesaplama kısmı (`compute_submission`) ayrı bir fonksiyona çıkarılarak, HTTP-dışı (WebSocket) çağrının kimlik doğrulama bağlamı olmadan çökmesi de ayrıca giderildi. Aşağıdaki akış artık gerçek koda uygundur.
:::

## Oyun Amacı
Oyuncu, sistem tarafından verilen **Lig (`league`)** bazında, yine sistemin belirlediği **Oyuncu Sayısı (`player_count`)** hakkını kullanarak, hedeflenen **İstatistik (`metric`)** için istenen **Hedef Sayıya (`target`)** en yakın sonucu elde etmeye çalışır.

## Bulmaca Üretim Algoritması (`GET /api/mode31/generate`)
Backend, bulmacayı **gerçek oyuncu verisi sorgulamadan**, tamamen rastgele sayı matematiğiyle üretir (bkz. `round_target`/`generate_puzzle` — bilinçli bir tasarım tercihi, `b7f7982` commit'inde DB sorgusundan bu yönteme geçildi):

1. **Lig (`league`)** 8 seçenekten rastgele seçilir: `GB1` (Premier League), `ES1` (La Liga), `IT1` (Serie A), `L1` (Bundesliga), `FR1` (Ligue 1), `TR1` (Süper Lig), `INT` (Milli Takımlar), `ALL` (Tüm Ligler).
2. **Oyuncu Sayısı (`player_count`)** yalnızca **3** ya da **5** olabilir.
3. **Metrik (`metric`):**
   - Lig `INT` ise: `goals`, `assists`, `caps` arasından.
   - Diğer tüm ligler için: `goals`, `assists`, `appearances`, `yellow_cards`, `red_cards` arasından. (`minutes_played` artık bir seçenek **değildir** — kaldırıldı.)
4. **Hedef değer (`target`):** Her metrik için sabit bir `(min, max)` aralığı vardır (örn. gol: 30-150, asist: 20-80, maç: 100-300, sarı kart: 20-70, kırmızı kart: 1-5, milli takım cap: 30-90). Sistem, `player_count` kadar rastgele sayıyı bu aralıktan çekip toplar, sonucu metriğe göre yukarı yuvarlar (dakika hariç 10'un katına, dakika varsa — ki artık yok — 100'ün katına).
5. `puzzle_id` (UUID) üretilir ama backend'de doğrulama için kullanılmaz (frontend'in kendi state takibi içindir).

::: tip Solvability notu
Hedef gerçek oyunculardan değil rastgele matematikten geldiği için, **tam isabet (distance=0) garanti edilmez** — bu modun doğası "hedefe mümkün olduğunca yaklaşmak" olduğundan, bu kasıtlı ve kabul edilebilir bir tasarımdır.
:::

## Oyuncu Doğrulama ("Dummy Engeli") — `POST /api/mode31/validate-single`
Kullanıcı bir kutuya oyuncu seçtiğinde frontend bu endpoint'i çağırır. `payload: {league, metric, player_id}`.
- `league == "INT"`: oyuncunun `player_national_stats` toplamı (`caps`) sıfırdan büyük değilse `{"valid": false, "message": "Bu oyuncu milli takımda oynamamış."}` döner ve kutuya yerleşmez.
- Diğer ligler: oyuncunun o ligdeki (`league == "ALL"` ise tüm liglerdeki) `player_club_stats.appearances` toplamı sıfırdan büyük değilse aynı şekilde reddedilir (`"Bu oyuncu bu ligde oynamamış."`).
- Geçerliyse `{"valid": true, "value": <toplam>}` döner ve frontend oyuncuyu kutuya yerleştirir.

Bu sayede hem kullanıcının bilmeden geçersiz bir seçim yapıp cezalandırılması engellenir, hem de "N oyuncu" şartının daha az geçerli oyuncuyla bypass edilmesi mümkün olmaz.

## Puanlama — `POST /api/mode31/validate`
Tüm kutular doldurulup gönderildiğinde backend, her oyuncunun ilgili metrikteki toplamını tekrar (güvenlik için sunucu tarafında) hesaplar, `total_sum`'ı bulur ve `distance = |target - total_sum|`, `deviation_percent = distance / max(1, target) * 100` üzerinden şu kesin kademeleri uygular:

| Sapma | XP | Tier |
|---|---|---|
| `distance == 0` (tam isabet) | **25 XP** | 0 |
| `deviation_percent ≤ 5%` | **25 XP** | 1 |
| `deviation_percent ≤ 15%` | **15 XP** | 2 |
| `deviation_percent ≤ 25%` | **10 XP** | 3 |
| `deviation_percent > 25%` | **5 XP** | 4 |

XP eklendikten sonra backend aynı istekte level-up kontrolü de yapar: `required_xp = 100 * level^1.5`; `xp >= required_xp` olduğu sürece `level += 1` ve `xp -= required_xp` döngüsü çalışır (birden fazla seviye birden atlanabilir).

## Online Mod (WebSocket, `game_mode: "mode31"`)
1. **Oda ve Eşleşme:** İki oyuncu eşleşir (bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)); backend `generate_puzzle()` ile **her iki oyuncuya da aynı bulmacayı** üretir ve `puzzle_ready` mesajıyla yayınlar.
2. **Süre:** Sunucu tarafında **90 saniyelik** kesin bir sayaç çalışır (bağlantı kopmalarında duraklar). Süre dolduğunda otomatik değerlendirme tetiklenir.
3. **Gönderim (kilitleme):** Bir oyuncu seçimlerini bitirip gönderdiğinde bu, o oyuncu için kilitlenir; rakip süresi bitene kadar (veya o da gönderene kadar) seçime devam edebilir. İki oyuncu da gönderdiğinde zamanlayıcı task'i iptal edilir ve değerlendirme hemen yapılır.
4. **Eksik gönderim = otomatik diskalifiye:** Bir oyuncu `player_count` kadar oyuncu seçmeden süre biterse, o oyuncunun mesafesi `999999` (sonsuz) kabul edilir — otomatik kaybeder.
5. **Kazanma ve Eşitlik:** Toplam skoru hedefe **en yakın olan** (küçük `distance`) kazanır. Mesafeler eşitse (ve ikisi de gerçekten gönderim yapmışsa, iki taraf da diskalifiye değilse), **ilk gönderen** (`timestamp` küçük olan) kazanır. İki taraf da eksik/diskalifiyeyse el **berabere** biter ve oda ücreti iade edilir (rake alınmaz, bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)).

## Kısıtlamalar ve Uç Durumlar
1. **Mükerrer Oyuncu Engeli:** Bir oyuncu birden fazla kutuya yerleştirilemez (frontend, zaten seçilmiş `player_id`'leri arama sonuçlarından hariç tutar).
2. **Geçersiz Oyuncu Uyarısı:** Yukarıda anlatılan "Dummy Engeli" ile korunur.
3. **Arama Çubuğu Şeffaflığı:** `SearchModal` filtreleme yapmaz, dünyadaki tüm oyuncuları getirir; kullanıcı kimin o ligde oynadığını `validate-single` geri bildiriminden öğrenir.

## Oynanış Akışı (UI/UX)
`frontend/screens/singleplayer/TargetScoreScreen.js` (tek oyunculu) ve `frontend/screens/multiplayer/MultiplayerTargetScoreScreen.js` (online) üzerinden ilerler:
1. Sayfanın üstünde seçilmiş lig ve hedef skor yazar (Örn: "Premier League (İngiltere) - Toplam 300 Gol").
2. Hedefin altında `player_count` (3 veya 5) kadar boş oyuncu barı yer alır.
3. Oyuncu boş bir bara tıkladığında `SearchModal` açılır; seçim yapıldığında `validate-single` çağrılır, geçersizse hata mesajı gösterilir ve kutu boş kalır.
4. Tüm kutular doldurulduktan sonra "Bitir" butonuna basılır, `validate` çağrılır ve sonuç ekranında (`TargetScoreResultScreen.js`) hedefe yakınlık, kazanılan XP ve (varsa) level-up animasyonu gösterilir.
