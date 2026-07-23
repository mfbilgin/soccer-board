# Top 10 Tahmin Modu — "İlk 10 Listesi"

Bir ligde/milli takımda/kulüpte tüm zamanların bir metrikte (gol, asist veya maç sayısı) **ilk 10** futbolcusunu tahmin etmeye dayanan bir hafıza ve bilgi yarışmasıdır.

**Durum:** Kodlandı ve çalışıyor (hem singleplayer hem online).

Online kısmının kod karşılığı: `backend/routers/pyramid.py`'den çıkarılan `generate_puzzle(db)` (singleplayer endpoint'i değiştirmeden, aynı mantığı multiplayer'la paylaşır), `backend/routers/multiplayer.py`'deki `top10_timer`/`top10_advance`/`finish_top10` (mevcut tier kuyruğu üzerinden `game_mode: "top10"` — yayına gitmeden önce `_top10_public_items` gizli hücrelerin ismini kırpar, aksi halde ilk paket cevapları ifşa ederdi), `frontend/screens/multiplayer/MultiplayerTop10Screen.js`.

Singleplayer akışının kod karşılığı `backend/routers/pyramid.py` (`/api/game/pyramid/generate`) ve `frontend/screens/singleplayer/PyramidScreen.js` dosyalarındadır — isimlendirme tarihsel bir nedenle "Pyramid" olarak kalmıştır, ama uyguladığı oyun burada anlatılan Top 10 modudur. [Piramit Sıralaması](/guide/game-modes/pyramid-ranking) sayfasındaki farklı (evet/hayır fikir belirtme) mod, ayrı bir konsepttir.

## Arayüz ve Kurallar
- Oyun ekranında alt alta dizilmiş **10 kutucuk** bulunur.
- İlk 3 kutucuk (sıralamadaki ilk 3 kişi) ipucu niteliğinde dolu olarak gelir.
- Oyuncuların **3 yanlış yapma hakkı** vardır (yalnızca offline modda geçerlidir — bkz. aşağı). 3 kere yanlış tahmin eden oyunu kaybeder.

## Liste Türleri (rastgele seçilir)
Bulmaca üretimi üç farklı liste türünden birini rastgele üretir:
1. **Kulüp Ligi:** Rastgele bir lig (Premier League, La Liga, Serie A, Ligue 1, Bundesliga, Süper Lig) + rastgele bir metrik (gol/asist/maç) — "Premier League'de En Çok Gol Atanlar" gibi.
2. **Milli Takım:** Milli takımlarda en çok gol atanlar listesi.
3. **Takım Bazlı:** Belirli bir popüler kulüp (Real Madrid, Barcelona, Fenerbahçe vb.) formasıyla en çok gol/asist/maç yapanlar.

## Offline (Tek Oyunculu) Mod
- Oyuncu, eksik olan 7 sırayı tahmin etmeye çalışır, **3 yanlış hakkı** vardır.
- Yanlış haklarını doldurmadan listedeki tüm oyuncuları tamamlarsa kazanır. Yarışma baskısı yoktur, süre sınırı yoktur.
- 3 yanlış hak biterse oyun biter, kalan hücreler "kaçırıldı" olarak kırmızıyla açılır.

## Online (Multiplayer) Mod
Turn-based, WebSocket üzerinden (`game_mode: "top10"`), [Multiplayer Core](/guide/game-modes/multiplayer-core)'daki ortak oda/eşleştirme altyapısını kullanır.

1. **Oda ve Eşleşme:** İki oyuncu eşleşir; sunucu üretilen **aynı listeyi** her iki oyuncuya da gösterir. Kim başlayacak rastgele belirlenir.
2. **3 Can Kuralı Online'da Geçerli Değildir:** Online modda can/hak limiti yoktur — bunun yerine sıra ve süre rekabeti vardır.
3. **Sıra ve Süre:** Sırası gelen oyuncunun bir isim yazması için **20 saniye** vardır.
4. **Doğru Tahmin:** İsim listede (gizli 7 hücrenin herhangi birinde) varsa, o hücre otomatik doğru sıraya yerleşir ve tahmin eden oyuncu **o hücrenin sıra numarası kadar puan** kazanır (10. sırayı bilen 10 puan, 1. sırayı bilen 1 puan — alt sıralar daha az bilindiği için daha değerlidir). Sıra karşı oyuncuya geçer.
5. **Yanlış Tahmin:** İsim listede yok veya zaten açılmış bir hücreye denk geliyorsa, o oyuncu 0 puan alır ve sıra karşı oyuncuya geçer (can kaybı yoktur, sadece sıra kaybı).
6. **Süre Dolumu:** O turda tahmin gelmezse otomatik olarak sıra karşı oyuncuya geçer.
7. **Bitiş Koşulu 1 — Tahta Dolar:** 7 gizli hücrenin tamamı açıldığında oyun biter; en çok puanı toplayan kazanır. Toplam puan eşitse berabere biter, oda ücreti iade edilir.
8. **Bitiş Koşulu 2 — Deadlock:** Art arda 2 tur (bir oyuncudan biri yanlış/süre-dolumu, hemen ardından diğerinden de yanlış/süre-dolumu) hiçbir doğru tahmin gelmezse, oyun erken sonlanır. Kalan hücreler açılır, o ana kadarki puanlarla kazanan belirlenir; puanlar eşitse berabere.
9. **Ödül:** Kazanan havuzun %90'ını alır (standart rake kuralı).

## Backend Sözleşmesi (online kısım)
- Bulmaca üretim fonksiyonu, mevcut singleplayer üretim mantığı yeniden kullanılarak WebSocket bağlamından da çağrılır.
- Multiplayer oda başlatma akışına `game_mode == "top10"` dalı, tur/süre yönetimi için [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki turn-timer deseniyle aynı mimaride bir zamanlayıcı, ve tur sonucu/puan durumunu değerlendiren bir fonksiyon eklenir.

## Kısıtlamalar ve Uç Durumlar
- **Sıra tahmini istenmez:** Oyuncu yalnızca ismi yazar; sistem doğru sıraya otomatik yerleştirir — hangi sırada olduğunu bilmek zorunda değildir, bu sürtünmeyi azaltır.
- **Eşadlılık:** Autocomplete ile resmi isim seçtirilir ([TicTacToe arama](/guide/game-modes/tictactoe-4x4)'daki `/search`-tarzı endpoint yeniden kullanılabilir).
- **Veri yeterliliği:** Seçilen lig/takım/kategori için en az 10 oyuncu bulunamazsa bulmaca yeniden üretilir (farklı bir liste türü/lig seçilerek).
- **Liste güncelliği:** "Tüm zamanlar" listeleri, veritabanındaki toplam istatistiklerin doğruluğuna bağlıdır.
