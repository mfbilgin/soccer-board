# Baş Harflerinden Futbolcu Tahmini — "Harf Düellosu"

Harf kısıtlamalarıyla hafızayı zorlayan, kelime türetme ve futbol bilgisini birleştiren spesifik bir mod.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir.
:::

## Tanım
Bilinen adı (`players.known_as`) belirli bir **harfle başlayıp** belirli bir **harfle biten** bir futbolcuyu ilk söyleyen/yazan kazanır.

## Online Mod Oynanışı
1. Maç başladığında sistem, her iki oyuncudan da rastgele **1'er harf** seçmesini ister (Örn: 1. Oyuncu **M**, 2. Oyuncu **A** seçer) — harf seçimi Türk alfabesindeki 29 harften rastgele sunulan 5 seçenek arasından yapılır (tamamen serbest 29 harf değil, her zaman çözümü garanti edilebilecek şekilde aşağıdaki kontrol algoritmasıyla filtrelenmiş 5 harf sunulur).
2. Sistem bu harfleri birleştirir. Kural: **Bilinen adı 1. oyuncunun harfiyle başlayıp, 2. oyuncunun harfiyle biten** bir futbolcu bulmak (Örn: **M**aradon**a**).
3. Her iki oyuncunun da tahmin yapabilmesi için **30 saniyesi** vardır.
4. Doğru oyuncuyu ilk yazan taraf turu kazanır. 30 saniye boyunca kimse bulamazsa o el berabere biter (oda ücreti iade edilir, kimse puan alamaz).
5. **Maç formatı:** [Find Player From Two](/guide/game-modes/find-player-from-two) ile aynı desende, **ilk 3 turu kazanan** (best-of-5) maçı kazanır.

## Çözülebilirlik Garantisi (kesin algoritma)
Rastgele iki bağımsız harfin kesişimi boş küme olabileceğinden ("Q" ile başlayıp "X" ile biten kimse yoktur), sistem **baştan itibaren yalnızca çözümü garanti edilen çiftler sunar**:
1. Backend, veritabanından rastgele bir oyuncu çeker, `known_as`'ının ilk harfini ve son harfini alır — bu harf çifti **tanım gereği çözümlüdür** (en az o oyuncunun kendisi cevaptır).
2. Bu şekilde 1. oyuncuya sunulacak "başlangıç harfi" havuzu ve 2. oyuncuya sunulacak "bitiş harfi" havuzu, veritabanından çekilen 5'er örnek oyuncudan türetilir.
3. Oyuncular kendi havuzlarından birer harf seçtiğinde, seçilen ikili **mutlaka** en az bir gerçek oyuncuyla eşleşir (çünkü her iki harf de zaten gerçek bir `known_as`'tan türetildi — ortak bir oyuncu paylaşmasalar bile, sistemin başlangıçta iki harfi **aynı** örnek oyuncudan alması bu garantiyi sağlar: 1. oyuncu ve 2. oyuncuya sunulan 5'erli havuzlar, backend'in seçtiği **aynı 5 örnek oyuncunun** ilk/son harflerinden oluşur, böylece hangi kombinasyon seçilirse seçilsin en az kendi kaynağı oyuncu geçerli bir cevaptır).

## Offline Mod Oynanışı
- Sistem yukarıdaki garantili algoritmayla kendisi rastgele 2 harf belirler (kullanıcıya seçim sorulmaz).
- Oyuncu, sistemin belirlediği harflerle başlayan ve biten bir oyuncu bulmaya çalışır. Süre kısıtlaması yoktur, pratik yapmak için idealdir. Yanlış tahmin sınırı yoktur; kullanıcı "Pes Et" derse doğru cevap (sistemin ürettiği kaynak oyuncu) gösterilir.

## Kısıtlamalar ve Uç Durumlar
- **Soyadı vs. tam ad:** Bazı oyuncular tek isimle bilinir (Ronaldinho, Neymar). `known_as` alanı zaten bu normalize edilmiş "bilinen isim"i tutar, ek bir işlem gerekmez.
- **Transkripsiyon:** Türkçe (İ/ı, ş, ç) ve diğer uluslararası karakterlerin normalizasyonu, [TicTacToe arama](/guide/game-modes/tictactoe-4x4)'da kullanılan `unidecode` normalizasyonuyla aynı şekilde yapılır — kullanıcı "İ" yerine "I" yazsa da kabul edilir.
- **Birden fazla geçerli cevap:** Bir harf çiftine uyan birden fazla oyuncu olabilir (örn. M...a); herhangi biri kabul edilir, "tek doğru cevap" diye bir kısıt yoktur.

## Backend İhtiyaçları (uygulanacak API/WebSocket sözleşmesi)
- `GET /api/game/initials-guess/letter-pools` → yukarıdaki algoritmayla üretilmiş, her biri 5 harf içeren iki ayrı havuz (`start_pool`, `end_pool`) döner.
- WebSocket `game_mode: "initials_guess"`, action `initials_guess_answer` → gelen isim `known_as ILIKE 'X%Y'` sorgusuyla (unidecode normalize edilmiş) doğrulanır; [Find Player From Two](/guide/game-modes/find-player-from-two)'daki buzzer handler deseniyle aynı şekilde ilk doğru cevabı işler.
