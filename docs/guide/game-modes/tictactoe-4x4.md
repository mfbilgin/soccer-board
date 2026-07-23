# Tic-Tac-Toe Modu (Takımlar ve Futbolcularla)

Bu mod, klasik Tic-Tac-Toe (XOX) oyununun futbol bilgisiyle harmanlanmış, taktiksel ve bilgiye dayalı bir versiyonudur. Oyuncular 4x4'lük bir matrisin kesişim noktalarındaki hücreleri doğru tahminler yaparak ele geçirmeye ve 3'lü bir seri (yatay, dikey veya çapraz) oluşturmaya çalışırlar.

**Durum:** Kodlanmış ve çalışıyor — hem singleplayer hem online.

## Oyun Amacı ve Matris Türleri
Matris 4x4 boyutundadır (1. satır ve 1. sütun başlıkları oluşturur, oynanabilir alan 3x3'tür). Oyun başladığında backend iki matris türünden birini üretir — `GET /api/game/tictactoe/grid?type=1|2`, `type` verilmezse rastgele seçilir:

### 1. Takım Matrisi (Type 1 — Team×Team)
- **Başlıklar:** 1. satır (3 adet) ve 1. sütun (3 adet) **takımlardan** oluşur.
- **Kesişim Görevi:** Kullanıcı boş bir hücreye tıkladığında, o hücrenin kesiştiği **her iki takımda da oynamış bir futbolcu** ismi girmek zorundadır.
- *Örnek:* Satır başlığı "Chelsea", Sütun başlığı "Arsenal" ise kullanıcı bu hücreyi almak için "Ashley Cole" veya "Cesc Fabregas" gibi iki takımın da formasını giymiş bir oyuncu seçmelidir.

### 2. Oyuncu Matrisi (Type 2 — Player×Player)
- **Başlıklar:** 1. satır (3 adet) ve 1. sütun (3 adet) **futbolculardan** oluşur.
- **Kesişim Görevi:** Kullanıcı boş bir hücreye tıkladığında, o hücrenin kesiştiği **her iki futbolcunun da (farklı zamanlarda veya aynı anda) forma giydiği ortak bir takımı** girmek zorundadır.
- *Örnek:* Satır başlığı "Cristiano Ronaldo", Sütun başlığı "Karim Benzema" ise "Real Madrid" doğru cevaptır.

## Izgara Üretim Algoritması
Sunucu açılışında, tüm süreç boyunca paylaşılan bir bellek içi önbellek kurulur: en çok maça çıkan **150 takım** ve en çok maça çıkan **150 oyuncu**, artı her takımın oynamış tüm oyuncularının kümesi ve her oyuncunun oynamış tüm takımlarının kümesi.

Izgara üretimi, bu 150'lik havuzdan en fazla **500 deneme** yaparak: rastgele bir "satır 1" seçer → onunla kesişen (ortak oyuncusu/takımı olan) adaylardan rastgele 3 "sütun" seçer → bu 3 sütunun üçüyle birden kesişen adaylardan rastgele 2 "satır" daha seçer. 500 denemede çözülebilir bir kombinasyon bulunamazsa hata döner (pratikte 150'lik popüler havuzda bu son derece nadirdir). Bu algoritma, **her hücrenin en az bir doğru cevabı olduğunu üretim anında garanti eder** — ayrı bir doğrulama adımına gerek yoktur.

## Puanlama ve Kazanma Koşulları

**Singleplayer (Tek Oyunculu) Akışı:**
- Kullanıcının amacı 3x3'lük tablonun tamamını (9 hücreyi) doldurmaktır.
- Kullanıcının **sınırsız deneme hakkı** vardır. Yanlış tahmin yaptığında herhangi bir can eksilmez, dilediği kadar farklı oyuncu/takım deneyebilir.
- **Pes Etme:** `POST /api/game/tictactoe/surrender` çağrılır (`grid_type`, `row_ids`, `col_ids`, `correct_count` gönderilir); backend o ana kadar doğru bilinen hücre sayısı × **10 XP** ekler, level-up kontrolü yapar ve boş kalan hücreler için örnek doğru cevapları döner (öğreticilik amaçlı).
- Yapılan her doğru hücre tahmini için **10 XP** kazanılır.

**Multiplayer (Online) Akışı ve Kuralları:**
Online mod sıra tabanlıdır (turn-based), WebSocket üzerinden (`game_mode: "tictactoe_1"` veya `"tictactoe_2"`).
1. **Oda ve Eşleşme:** İki oyuncu eşleşir. Kim başlayacak (**X**) kim ikinci olacak (**O**) rastgele belirlenir.
2. **Sıra ve Süre:** Sırası gelen oyuncunun bir hücre seçip tahmin yapması için sunucu tarafında **30 saniye** çalışır; bağlantı kopuklarında duraklar.
3. **Doğru/Yanlış Tahmin:**
   - Doğru tahmin → hücre oyuncunun sembolüyle (X/O) işaretlenir, sıra rakibe geçer.
   - Yanlış tahmin veya dolu hücre seçimi → istek yok sayılır (hücre boş kalır, sıra değişmez).
   - **Süre dolumu = otomatik pas:** Süresi dolan oyuncu için otomatik olarak "pas" tetiklenir.
4. **Manuel Pas Geçme:** Oyuncu "Pas" butonuyla sırasını anında rakibe devredebilir.
5. **Kazanma Koşulu:** Yatay, dikey veya çapraz 3 hücreyi işaretleyen (klasik Tic-Tac-Toe kuralı) oyuncu anında maçı kazanır.
6. **Tahta Dolması:** 9 hücrenin tamamı dolduğunda kimse 3'lü seri yapmadıysa, tahtada en çok hücresi olan kazanır; hücre sayıları eşitse berabere biter.

**Kilitlenme (Deadlock) Akışı:**
1. **1. Pas:** Bir oyuncu pas geçer (manuel veya süre dolumuyla otomatik).
2. **2. Pas:** Diğer oyuncu da (araya doğru bir tahmin girmeden) pas geçerse **Deadlock** anında tetiklenir.
3. **Sonuçlandırma:** Oyun anında biter; tıpkı tahta dolmuş gibi tahtada en çok hücresi olan kazanır, eşitlikte berabere.

**Beraberlik/Kazanansız Sonuç ve Ödül:** Gerçek bir 3'lü seriyle biten maçta kazanan, havuzun %90'ını alır (bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)). Kazanan yoksa (tahta doluyla veya deadlock ile berabere), oda ücreti her iki oyuncuya da iade edilir, rake kesilmez. Oyun bitiminde boş kalan hücrelerin cevapları her iki oyuncuya da gösterilir.

## Kısıtlamalar ve Uç Durumlar
1. **Mükerrer Kullanım Engeli Yoktur:** Aynı oyuncu/takım tahtada birden fazla hücrenin doğru cevabı olabilir; sistem bunu engellemez, kullanıcı isterse aynı ismi birden çok hücreye yazabilir. Bu, ızgara üretim algoritmasının doğası gereği kesişimi doğru olan her cevabın kabul edilmesiyle basitliği korur.
2. **Arama:** `GET /api/game/tictactoe/search?q=...&type=1|2`, önce SQL tabanlı önceliklendirilmiş arama (tam eşleşme > başlayan > kelime başı > içeren, aktif/milli takım popülerliğine göre sıralı) yapar; 10 sonuçtan azsa bulanık arama (skor eşiği **60**) sonuçları eklenir. Türkçe karakter/aksan farkları normalize edilir.
3. **Cache tazeliği:** Popülerlik önbelleği yalnızca sunucu açılışında bir kez kurulur (bkz. [Database Structure](/guide/database)). Veritabanına yeni oyuncu/istatistik eklense bile ızgara üretimi backend yeniden başlatılana kadar eski önbelleği kullanır.

## Oynanış Akışı (UI/UX)
1. **Oyun Ekranı:** Merkezde 4x4 (oynanabilir alan 3x3) bir ızgara yer alır.
2. **Başlıklar:** Takım matrisinde kulüp logoları (kısa isim önceliğiyle), oyuncu matrisinde oyuncu isimleri kullanılır.
3. **Hücre Seçimi:** Kullanıcı boş bir hücreye dokunduğunda arama modalı açılır.
4. **Animasyonlar:** Online modda rakip doğru tahmin yaptığında hücre rakibin sembolüyle dolar; seriyi tamamlayan çizgi görsel bir efektle vurgulanır.
