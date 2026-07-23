# Top 10 Tahmin Modu — "İlk 10 Listesi"

Bir ligde/milli takımda/kulüpte tüm zamanların bir metrikte (gol, asist veya maç sayısı) **ilk 10** futbolcusunu tahmin etmeye dayanan bir hafıza ve bilgi yarışmasıdır.

::: tip Uygulama durumu ve isimlendirme notu
Singleplayer akışı kodda **`backend/routers/pyramid.py`** (`/api/game/pyramid/generate`) ve **`frontend/screens/singleplayer/PyramidScreen.js`** olarak yaşıyor — isim tarihsel bir nedenle "Pyramid" kalmış, ama gerçekte uyguladığı oyun tam olarak burada anlatılan Top 10 modudur. [Piramit Sıralaması](/guide/game-modes/pyramid-ranking) sayfasındaki farklı (evet/hayır fikir belirtme) mod ise ayrı bir konsepttir ve henüz kodlanmamıştır. **Online kısım (aşağıda) henüz hiç kodlanmamıştır** — `multiplayer.py`'de bu moda dair hiçbir referans yoktur; aşağıdaki tasarım doğrudan uygulanabilir bir spesifikasyondur.
:::

## Arayüz ve Kurallar
- Oyun ekranında alt alta dizilmiş **10 kutucuk** bulunur.
- İlk 3 kutucuk (sıralamadaki ilk 3 kişi) ipucu niteliğinde dolu olarak gelir.
- Oyuncuların **3 yanlış yapma hakkı** vardır (yalnızca offline modda geçerlidir — bkz. aşağı). 3 kere yanlış tahmin eden oyunu kaybeder.

## Liste Türleri (mevcut backend'de rastgele seçilir)
`pyramid.py`'deki `generate_pyramid` üç farklı liste türünden birini rastgele üretir:
1. **Kulüp Ligi:** Rastgele bir lig (Premier League, La Liga, Serie A, Ligue 1, Bundesliga, Süper Lig) + rastgele bir metrik (gol/asist/maç) — "Premier League'de En Çok Gol Atanlar" gibi.
2. **Milli Takım:** Milli takımlarda en çok gol atanlar listesi.
3. **Takım Bazlı:** Belirli bir popüler kulüp (Real Madrid, Barcelona, Fenerbahçe vb.) formasıyla en çok gol/asist/maç yapanlar.

## Offline (Tek Oyunculu) Mod
- Oyuncu, eksik olan 7 sırayı tahmin etmeye çalışır, **3 yanlış hakkı** vardır.
- Yanlış haklarını doldurmadan listedeki tüm oyuncuları tamamlarsa kazanır. Yarışma baskısı yoktur, süre sınırı yoktur.
- 3 yanlış hak biterse oyun biter, kalan hücreler "kaçırıldı" olarak kırmızıyla açılır.

## Online (Multiplayer) Mod — tam spesifikasyon
Turn-based, WebSocket üzerinden (`game_mode: "top10"`), [Multiplayer Core](/guide/game-modes/multiplayer-core)'daki ortak oda/eşleştirme altyapısını kullanır.

1. **Oda ve Eşleşme:** İki oyuncu eşleşir; backend `generate_pyramid()` ile üretilen **aynı listeyi** her iki oyuncuya da gösterir. Kim başlayacak rastgele belirlenir (TicTacToe'daki `random.random() > 0.5` deseniyle aynı).
2. **3 Can Kuralı Online'da Geçerli Değildir:** Online modda can/hak limiti yoktur — bunun yerine **sıra ve süre** rekabeti vardır (taslak_plan.txt'teki orijinal tasarıma sadık kalınmıştır).
3. **Sıra ve Süre:** Sırası gelen oyuncunun bir isim yazması için **20 saniye** vardır (TicTacToe'nun 30 saniyesinden daha kısa — çünkü her turda tek bir tahmin yapılıyor, tüm tahtayı doldurmuyor).
4. **Doğru Tahmin:** İsim listede (gizli 7 hücrenin herhangi birinde) varsa, o hücre otomatik doğru sıraya yerleşir ve tahmin eden oyuncu **o hücrenin sıra numarası kadar puan** kazanır (10. sırayı bilen 10 puan, 1. sırayı bilen 1 puan — alt sıralar daha az bilindiği için daha değerlidir). Sıra karşı oyuncuya geçer.
5. **Yanlış Tahmin:** İsim listede yok veya zaten açılmış bir hücreye denk geliyorsa, o oyuncu **0 puan** alır ve sıra karşı oyuncuya geçer (can kaybı yoktur, sadece sıra kaybı).
6. **Süre Dolumu:** O turda tahmin gelmezse otomatik olarak sıra karşı oyuncuya geçer (TicTacToe'daki `tictactoe_timer`/otomatik pas deseniyle aynı mantık, sunucu taraflı).
7. **Bitiş Koşulu 1 — Tahta Dolar:** 7 gizli hücrenin tamamı açıldığında oyun biter; en çok puanı toplayan kazanır. Toplam puan eşitse **berabere** biter, oda ücreti iade edilir.
8. **Bitiş Koşulu 2 — Deadlock:** Art arda 2 tur (bir oyuncudan biri yanlış/süre-dolumu, hemen ardından diğerinden de yanlış/süre-dolumu) hiçbir doğru tahmin gelmezse, oyun **erken sonlanır** — TicTacToe'daki deadlock kuralıyla birebir aynı mantık. Kalan hücreler açılır (öğreticilik), o ana kadarki puanlarla kazanan belirlenir; puanlar eşitse berabere.
9. **Ödül:** Kazanan havuzun %90'ını alır (standart rake kuralı).

### Gerekli backend değişikliği
- `pyramid.py`'ye `generate_pyramid`'in `db: Session` parametresini WebSocket bağlamından da çağrılabilir hale getirmek dışında ek bir değişiklik gerekmez — fonksiyon zaten saf bir üretim fonksiyonu.
- `multiplayer.py`'nin `initialize_game_state` fonksiyonuna `room.game_mode == "top10"` dalı eklenmesi, `mode31_timer`/`tictactoe_timer` desenine benzer bir `top10_timer` ve tur/puan durumunu tutan bir `evaluate_top10_turn` fonksiyonu yazılması gerekir.

## Kısıtlamalar ve Uç Durumlar
- **Sıra tahmini istenmez:** Oyuncu yalnızca ismi yazar; sistem doğru sıraya otomatik yerleştirir — hangi sırada olduğunu bilmek zorunda değildir, bu sürtünmeyi azaltır.
- **Eşadlılık:** Autocomplete ile resmi isim seçtirilir (bkz. [TicTacToe arama](/guide/game-modes/tictactoe-4x4) ile aynı `/search`-tarzı endpoint yeniden kullanılabilir).
- **Veri yeterliliği:** Backend, seçilen lig/takım/kategori için en az 10 oyuncu bulamazsa (`len(top_players) < 10`) `500` hatası döner — bu durumda frontend/`generate` çağrısını tekrar dener (yeni bir liste türü/lig seçilerek).
- **Liste güncelliği:** "Tüm zamanlar" listeleri, veritabanındaki `player_club_stats`/`player_national_stats` toplamlarının doğruluğuna bağlıdır.
