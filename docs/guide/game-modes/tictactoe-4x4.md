# Tic-Tac-Toe Modu (Takımlar ve Futbolcularla)

Bu mod, klasik Tic-Tac-Toe (XOX) oyununun futbol bilgisiyle harmanlanmış, taktiksel ve bilgiye dayalı bir versiyonudur. Oyuncular 4x4'lük bir matrisin kesişim noktalarındaki hücreleri doğru tahminler yaparak ele geçirmeye ve 3'lü bir seri (yatay, dikey veya çapraz) oluşturmaya çalışırlar.

::: danger İki bilinen bug — online mod şu an oynanamıyor
1. **Multiplayer tahmin tamamen çalışmıyor:** `backend/routers/multiplayer.py` satır 464, `engine.validate_answer(grid["type"], row_id, col_id, entity_id)` çağırıyor. Ama `tictactoe.py`'de böyle bir metod **yok** — gerçek metod adı `validate_guess(row_id, col_id, guess_id, grid_type)` (hem isim hem parametre sırası farklı). Sonuç: online TicTacToe'da yapılan **her tahmin** `AttributeError` ile çöküyor. **Kesin düzeltme:** o satırı `engine.validate_guess(row_id, col_id, entity_id, grid["type"])` yapmak yeterli.
2. **Cevap açma (`get_answers`) Takım×Takım tipinde çöküyor:** `tictactoe.py`'deki `get_answers`, grid tipi 1 (Takım×Takım) için `self.popular_player_ids` alanını kullanıyor ama bu alan `__init__`'te hiç atanmamış (yalnızca `elite_player_ids`, `popular_team_ids`, `team_players`, `player_teams` cache'leniyor). Bu, hem singleplayer "pes et" akışını (`POST /api/game/tictactoe/surrender`) hem de multiplayer'da oyun bittiğinde cevapları açma akışını (`evaluate_tictactoe_winner`) tip-1 gridlerde çökertir. **Kesin düzeltme:** `self.popular_player_ids.index(...)` yerine zaten var olan `self.elite_player_ids.index(...)` kullanmak (aynı amaca hizmet ediyor: popülerliğe göre sıralı oyuncu ID listesi).

Tek oyunculu (Singleplayer) tahmin akışı (`POST /api/game/tictactoe/guess`) bu bug'lardan etkilenmez, doğru metodu doğru parametrelerle çağırıyor.
:::

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

## Izgara Üretim Algoritması (kesin, kodda doğrulandı)
`TicTacToeEngine`, sunucu açılışında **tüm süreç boyunca paylaşılan bir bellek içi önbellek** kurar (`main.py`'nin `startup` event'i): `player_club_stats` tablosundan en çok maça çıkan **150 takım** (`popular_team_ids`) ve en çok maça çıkan **150 oyuncu** (`elite_player_ids`), artı her takımın oynamış tüm oyuncularının kümesi (`team_players`) ve her oyuncunun oynamış tüm takımlarının kümesi (`player_teams`).

Izgara üretimi (`generate_type1_grid` / `generate_type2_grid`), bu 150'lik havuzdan en fazla **500 deneme** yaparak: rastgele bir "satır 1" seçer → onunla kesişen (ortak oyuncusu/takımı olan) adaylardan rastgele 3 "sütun" seçer → bu 3 sütunun **üçüyle birden** kesişen adaylardan rastgele 2 "satır" daha seçer. 500 denemede çözülebilir bir kombinasyon bulunamazsa `500` hatası döner (pratikte 150'lik popüler havuzda bu son derece nadirdir). Bu algoritma, **her hücrenin en az bir doğru cevabı olduğunu üretim anında garanti eder** — ayrı bir doğrulama adımına gerek yoktur.

## Puanlama ve Kazanma Koşulları

**Singleplayer (Tek Oyunculu) Akışı:**
- Kullanıcının amacı 3x3'lük tablonun tamamını (9 hücreyi) doldurmaktır.
- Kullanıcının **sınırsız deneme hakkı** vardır. Yanlış tahmin yaptığında herhangi bir can eksilmez, dilediği kadar farklı oyuncu/takım deneyebilir.
- **Pes Etme:** `POST /api/game/tictactoe/surrender` çağrılır (`grid_type`, `row_ids`, `col_ids`, `correct_count` gönderilir); backend o ana kadar doğru bilinen hücre sayısı × **10 XP** ekler ve boş kalan hücreler için örnek doğru cevapları döner (öğreticilik amaçlı).
- Yapılan her doğru hücre tahmini için **10 XP** kazanılır (toplamı frontend tarafında tutulur, `surrender` çağrısında backend'e bildirilir).
- 9 hücrenin tamamı hatasız doldurulursa ekstra bir **Kusursuzluk Bonusu** verilmesi tasarlanmıştır; mevcut backend'de bu bonus ayrı bir endpoint/parametre olarak **henüz yok** — 9/9 tamamlanan bir oyunda frontend, tüm doğru tahminlerin XP'sini (`correct_count * 10` = 90 XP) `surrender` endpoint'i üzerinden gönderir. Ayrı bir "kusursuzluk" bonusu eklenecekse `surrender` endpoint'ine `is_perfect: bool` alanı eklenip ekstra sabit XP (örn. +50) verilmesi en basit çözümdür.

**Multiplayer (Online) Akışı ve Kuralları:**
Online mod sıra tabanlıdır (turn-based), WebSocket üzerinden (`game_mode: "tictactoe_1"` veya `"tictactoe_2"`).
1. **Oda ve Eşleşme:** İki oyuncu eşleşir. Kim başlayacak (**X**) kim ikinci olacak (**O**) rastgele (`random.random() > 0.5`) belirlenir.
2. **Sıra ve Süre:** Sırası gelen oyuncunun bir hücre seçip tahmin yapması için sunucu tarafında **30 saniye** çalışır (`turn_end_time`); bağlantı kopuklarında duraklar.
3. **Doğru/Yanlış Tahmin:**
   - Doğru tahmin → hücre oyuncunun sembolüyle (X/O) işaretlenir, `consecutive_passes` sıfırlanır, sıra rakibe geçer.
   - Yanlış tahmin veya dolu hücre seçimi → istek sessizce yok sayılır (hücre boş kalır, sıra **değişmez** — oyuncu doğru cevap bulana veya süresi bitene kadar aynı hücrede deneme hakkı hakkı sürer; not: hücre seçimi değiştirmek istemcinin sorumluluğundadır).
   - **Süre dolumu = otomatik pas:** `tictactoe_timer`, süresi dolan oyuncu için otomatik olarak "pas" (`tictactoe_pass(auto=True)`) tetikler.
4. **Manuel Pas Geçme:** Oyuncu "Pas" butonuyla sırasını anında rakibe devredebilir (20/30 saniye beklemeden).
5. **Kazanma Koşulu:** Yatay, dikey veya çapraz 3 hücreyi işaretleyen (klasik Tic-Tac-Toe kuralı) oyuncu **anında** maçı kazanır (`check_tictactoe_win`).
6. **Tahta Dolması:** 9 hücrenin tamamı dolduğunda kimse 3'lü seri yapmadıysa, tahtada **en çok hücresi olan** kazanır; hücre sayıları eşitse **berabere** biter.

**Kilitlenme (Deadlock) Akışı:**
1. **1. Pas:** Bir oyuncu pas geçer (manuel veya süre dolumuyla otomatik). `consecutive_passes = 1`.
2. **2. Pas:** Diğer oyuncu da (araya doğru bir tahmin girmeden) pas geçerse `consecutive_passes = 2` olur ve **Deadlock** anında tetiklenir.
3. **Sonuçlandırma:** Oyun anında biter; tıpkı tahta dolmuş gibi tahtada **en çok hücresi olan** kazanır, eşitlikte berabere.

**Beraberlik/Kazanansız Sonuç ve Ödül:** Gerçek bir 3'lü seriyle biten maçta kazanan, havuzun **%90'ını** alır (bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)). Kazanan yoksa (tahta doluyla veya deadlock ile berabere), **oda ücreti her iki oyuncuya da iade edilir**, rake kesilmez. Oyun bitiminde boş kalan hücrelerin cevapları (`get_answers`, yukarıdaki bug'a dikkat) her iki oyuncuya da gösterilir.

## Kısıtlamalar ve Uç Durumlar
1. **Mükerrer Kullanım Engeli:** Bu, ızgara üretim algoritmasının doğası gereği garanti edilmez — aynı oyuncu/takım tahtada birden fazla hücrenin doğru cevabı olabilir; sistem bunu **engellemez**, kullanıcı isterse aynı ismi birden çok hücreye yazabilir. (Önceki taslaklarda "bir kez kullanılabilir" kısıtı öneriliyordu; mevcut backend'de böyle bir kontrol **yok** ve kesin karar olarak eklenmeyecektir — kesişimi doğru olan her cevap kabul edilir, bu basitliği korur.)
2. **Arama:** `GET /api/game/tictactoe/search?q=...&type=1|2`, önce SQL tabanlı önceliklendirilmiş arama (tam eşleşme > başlayan > kelime başı > içeren, aktif/milli takım popülerliğine göre sıralı) yapar; 10 sonuçtan azsa `rapidfuzz` ile (skor eşiği **60**) bulanık arama sonuçları eklenir. Türkçe karakter/aksan farkları `unidecode` ile normalize edilir.
3. **Cache tazeliği:** `TicTacToeEngine`'in popülerlik önbelleği yalnızca **sunucu açılışında bir kez** kurulur (bkz. [Database Structure](/guide/database) — restart uyarısı). Veritabanına yeni oyuncu/istatistik eklense bile ızgara üretimi backend yeniden başlatılana kadar eski önbelleği kullanır.

## Oynanış Akışı (UI/UX)
1. **Oyun Ekranı:** Merkezde 4x4 (oynanabilir alan 3x3) bir ızgara yer alır.
2. **Başlıklar:** Takım matrisinde kulüp logoları (`short_name` önceliğiyle), oyuncu matrisinde oyuncu isimleri (`known_as`) kullanılır.
3. **Hücre Seçimi:** Kullanıcı boş bir hücreye dokunduğunda `SearchModal` açılır; arama kutusu yukarıdaki `/search` endpoint'ini çağırır.
4. **Animasyonlar:** Online modda rakip doğru tahmin yaptığında hücre rakibin sembolüyle dolar; seriyi tamamlayan çizgi görsel bir efektle vurgulanır.
