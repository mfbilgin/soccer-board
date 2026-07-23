# İstatistik Hedefleri Modu (Stats Target / "Kariyer İstatistiği Avı")

Kullanıcının, sistemin verdiği sabit sayıda futbolcuyla, belirli bir kapsamda (lig veya milli takım) verilen bir istatistik hedefine **olabildiğince yakınlaşmaya** çalıştığı bir moddur. Amaç hedefi aşmak değil, hedefe tam olarak (ya da olabildiğince yakın) ulaşmaktır.

**Durum:** Singleplayer kodlanmış ve çalışıyor. Online (multiplayer) kısmı da kodlanmış ve çalışıyor.

## Oyun Amacı
Oyuncu, sistem tarafından verilen **Lig (`league`)** bazında, yine sistemin belirlediği **Oyuncu Sayısı (`player_count`)** hakkını kullanarak, hedeflenen **İstatistik (`metric`)** için istenen **Hedef Sayıya (`target`)** en yakın sonucu elde etmeye çalışır.

## Bulmaca Üretim Algoritması (`GET /api/mode31/generate`)
Bulmaca, gerçek oyuncu verisi sorgulanmadan, tamamen rastgele sayı matematiğiyle üretilir:

1. **Lig (`league`)** 8 seçenekten rastgele seçilir: `GB1` (Premier League), `ES1` (La Liga), `IT1` (Serie A), `L1` (Bundesliga), `FR1` (Ligue 1), `TR1` (Süper Lig), `INT` (Milli Takımlar), `ALL` (Tüm Ligler).
2. **Oyuncu Sayısı (`player_count`)** yalnızca **3** ya da **5** olabilir.
3. **Metrik (`metric`):**
   - Lig `INT` ise: `goals`, `assists`, `caps` arasından.
   - Diğer tüm ligler için: `goals`, `assists`, `appearances`, `yellow_cards`, `red_cards` arasından.
4. **Hedef değer (`target`):** Her metrik için sabit bir `(min, max)` aralığı vardır (gol: 30-150, asist: 20-80, maç: 100-300, sarı kart: 20-70, kırmızı kart: 1-5, milli takım cap: 30-90). Sistem, `player_count` kadar rastgele sayıyı bu aralıktan çekip toplar, sonucu 10'un katına yukarı yuvarlar.

Hedef gerçek oyunculardan değil rastgele matematikten geldiği için tam isabet (distance=0) garanti edilmez — bu modun doğası "hedefe mümkün olduğunca yaklaşmak" olduğundan, bu kasıtlı bir tasarımdır.

## Oyuncu Doğrulama ("Dummy Engeli") — `POST /api/mode31/validate-single`
Kullanıcı bir kutuya oyuncu seçtiğinde bu endpoint çağrılır. `payload: {league, metric, player_id}`.
- `league == "INT"`: oyuncunun milli takım cap toplamı sıfırdan büyük değilse `{"valid": false, "message": "Bu oyuncu milli takımda oynamamış."}` döner ve kutuya yerleşmez.
- Diğer ligler: oyuncunun o ligdeki (`league == "ALL"` ise tüm liglerdeki) toplam maç sayısı sıfırdan büyük değilse aynı şekilde reddedilir (`"Bu oyuncu bu ligde oynamamış."`).
- Geçerliyse `{"valid": true, "value": <toplam>}` döner ve oyuncu kutuya yerleşir.

Bu sayede hem kullanıcının bilmeden geçersiz bir seçim yapıp cezalandırılması engellenir, hem de "N oyuncu" şartının daha az geçerli oyuncuyla bypass edilmesi mümkün olmaz.

## Puanlama — `POST /api/mode31/validate`
Tüm kutular doldurulup gönderildiğinde, her oyuncunun ilgili metrikteki toplamı sunucu tarafında yeniden hesaplanır, `total_sum` bulunur ve `distance = |target - total_sum|`, `deviation_percent = distance / max(1, target) * 100` üzerinden şu kademeler uygulanır:

| Sapma | XP | Tier |
|---|---|---|
| `distance == 0` (tam isabet) | **25 XP** | 0 |
| `deviation_percent ≤ 5%` | **25 XP** | 1 |
| `deviation_percent ≤ 15%` | **15 XP** | 2 |
| `deviation_percent ≤ 25%` | **10 XP** | 3 |
| `deviation_percent > 25%` | **5 XP** | 4 |

XP eklendikten sonra aynı istekte level-up kontrolü de yapılır: `required_xp = 100 * level^1.5`; `xp >= required_xp` olduğu sürece `level += 1` ve `xp -= required_xp` uygulanır (birden fazla seviye birden atlanabilir). Bu leveling mantığı tüm modlarda ortak kullanılan tek bir fonksiyondadır (bkz. [Level Sistemi](/guide/systems/level-system-avatars)).

## Online Mod (WebSocket, `game_mode: "mode31"`)
1. **Oda ve Eşleşme:** İki oyuncu eşleşir (bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)); sunucu her iki oyuncuya da **aynı bulmacayı** üretir ve yayınlar.
2. **Süre:** Sunucu tarafında **90 saniyelik** bir sayaç çalışır (bağlantı kopmalarında duraklar). Süre dolduğunda otomatik değerlendirme tetiklenir.
3. **Gönderim (kilitleme):** Bir oyuncu seçimlerini bitirip gönderdiğinde bu, o oyuncu için kilitlenir; rakip süresi bitene kadar (veya o da gönderene kadar) seçime devam edebilir. İki oyuncu da gönderdiğinde değerlendirme hemen yapılır.
4. **Eksik gönderim = otomatik diskalifiye:** Bir oyuncu `player_count` kadar oyuncu seçmeden süre biterse, o oyuncunun mesafesi sonsuz kabul edilir — otomatik kaybeder.
5. **Kazanma ve Eşitlik:** Toplam skoru hedefe **en yakın olan** (küçük mesafe) kazanır. Mesafeler eşitse (ve iki taraf da gerçekten gönderim yapmışsa), **ilk gönderen** kazanır. İki taraf da eksik/diskalifiyeyse el **berabere** biter ve oda ücreti iade edilir.
6. Online modda XP verilmez, yalnızca Chip (ödül havuzu) ve Rating (ELO) değişir.

## Kısıtlamalar ve Uç Durumlar
1. **Mükerrer Oyuncu Engeli:** Bir oyuncu birden fazla kutuya yerleştirilemez.
2. **Geçersiz Oyuncu Uyarısı:** Yukarıda anlatılan "Dummy Engeli" ile korunur.
3. **Arama Çubuğu Şeffaflığı:** Arama filtreleme yapmaz, dünyadaki tüm oyuncuları getirir; kullanıcı kimin o ligde oynadığını doğrulama geri bildiriminden öğrenir.

## Oynanış Akışı (UI/UX)
`frontend/screens/singleplayer/TargetScoreScreen.js` (tek oyunculu) ve `frontend/screens/multiplayer/MultiplayerTargetScoreScreen.js` (online) üzerinden ilerler:
1. Sayfanın üstünde seçilmiş lig ve hedef skor yazar (Örn: "Premier League (İngiltere) - Toplam 300 Gol").
2. Hedefin altında `player_count` (3 veya 5) kadar boş oyuncu barı yer alır.
3. Oyuncu boş bir bara tıkladığında arama modalı açılır; seçim yapıldığında doğrulama çağrılır, geçersizse hata mesajı gösterilir ve kutu boş kalır.
4. Tüm kutular doldurulduktan sonra "Bitir" butonuna basılır, sonuç ekranında hedefe yakınlık, kazanılan XP ve (varsa) level-up animasyonu gösterilir.
