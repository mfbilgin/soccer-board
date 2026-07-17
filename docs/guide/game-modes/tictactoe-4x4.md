# Tic-Tac-Toe Modu (Takımlar ve Futbolcularla)

Bu mod, klasik Tic-Tac-Toe (XOX) oyununun futbol bilgisiyle harmanlanmış, taktiksel ve bilgiye dayalı bir versiyonudur. Oyuncular 4x4'lük bir matrisin kesişim noktalarındaki hücreleri doğru tahminler yaparak ele geçirmeye ve 3'lü bir seri (yatay, dikey veya çapraz) oluşturmaya çalışırlar.

## Oyun Amacı ve Matris Türleri
Matris 4x4 boyutundadır (1. satır ve 1. sütun başlıkları oluşturur, oynanabilir alan 3x3'tür). Oyun başladığında sistem iki farklı matris türünden birini rastgele seçer veya oyuncuya seçtirir:

### 1. Takım Matrisi (Team Matrix)
- **Başlıklar:** 1. satır (3 adet) ve 1. sütun (3 adet) **Takımlardan** (Kulüplerden) oluşur.
- **Kesişim Görevi:** Kullanıcı boş bir hücreye tıkladığında, o hücrenin kesiştiği **her iki takımda da oynamış bir futbolcu** ismi girmek zorundadır.
- *Örnek:* Satır başlığı "Chelsea", Sütun başlığı "Arsenal" ise kullanıcı bu hücreyi almak için "Ashley Cole" veya "Cesc Fabregas" gibi iki takımın da formasını giymiş bir oyuncu seçmelidir.

### 2. Oyuncu Matrisi (Player Matrix)
- **Başlıklar:** 1. satır (3 adet) ve 1. sütun (3 adet) **Futbolculardan** oluşur.
- **Kesişim Görevi:** Kullanıcı boş bir hücreye tıkladığında, o hücrenin kesiştiği **her iki futbolcunun da kariyerlerinde (farklı zamanlarda veya aynı anda) oynadığı ortak bir takımı** girmek zorundadır.
- *Örnek:* Satır başlığı "Cristiano Ronaldo", Sütun başlığı "Karim Benzema" ise kullanıcı bu hücreyi almak için "Real Madrid" seçebilir. Satır başlığı "Neymar", Sütun başlığı "Lionel Messi" ise "Barcelona" veya "PSG" seçilebilir.

## Puanlama ve Kazanma Koşulları

**Singleplayer (Tek Oyunculu) Akışı:**
- Kullanıcının amacı 3x3'lük tablonun tamamını (9 hücreyi) doldurmaktır.
- Kullanıcının **sınırsız deneme hakkı** vardır. Yanlış tahmin yaptığında herhangi bir can eksilmez, dilediği kadar farklı oyuncu/takım deneyebilir.
- **Pes Etme (Tıkanma Çözümü):** Eğer oyuncu tahtadaki kalan hücreleri bilmiyorsa "Bitir / Pes Et" butonuna basarak oyunu sonlandırabilir. Bu durumda sadece o ana kadar bildiği hücrelerin XP'sini alır. Oyun bitiminde boş kalan hücreler için sistem birer "örnek doğru cevap" göstererek oyuncunun bilgilenmesini sağlar.
- Yapılan her doğru hücre tahmini için **10 XP** kazanılır.
- Eğer 9 hücrenin tamamı hatasız doldurulursa ekstra **50 XP Kusursuzluk Bonusu** verilir.

**Multiplayer (Online) Akışı ve Kuralları:**
Online mod Sıra Tabanlıdır (Turn-based).
1. **Oda ve Eşleşme:** İki oyuncu eşleşir. Yazı-tura mekaniği ile kimin ilk başlayacağı (X) ve kimin ikinci olacağı (O) belirlenir.
2. **Sıra ve Süre:** Sırası gelen oyuncunun bir hücre seçip tahminini yapması için **30 Saniyesi** vardır.
3. **Doğru/Yanlış Tahmin ve Pas Geçme:** 
   - Oyuncu doğru tahmin yaparsa o hücre kendi sembolüyle (X veya O) işaretlenir. Sıra rakibe geçer.
   - Oyuncu yanlış tahmin yaparsa, o hücre boş kalır ve oyuncu sırasını kaybeder. Sıra rakibe geçer.
   - **Tıkanma Çözümü (Pas Geçme):** Eğer oyuncu boş hücrelerin hiçbirinin cevabını bilmiyorsa 20 saniye beklemek yerine "Pas" butonuna basarak sırasını anında rakibe devredebilir (veya süre biterse de otomatik pas geçmiş sayılır).
4. **Kazanma Koşulu:** Yatay, dikey veya çapraz olarak 3 hücresini yan yana dizen (Klasik Tic-Tac-Toe kuralı) ilk oyuncu **maçı kazanır**.
5. **Eşitlik ve Oyunun Kilitlenmesi (Deadlock) Durumu:** 
   - Tahtadaki tüm 9 hücre dolduğunda kimse 3'lü seri yapamadıysa tahtada en çok hücresi olan kazanır. Eşitlik varsa beraberlik olur.
   
**Kilitlenme (Deadlock) Akışı:**
Eğer tahtada hala boş hücreler olmasına rağmen iki oyuncu da cevapları bulamıyorsa oyun şu şekilde kilitlenir ve sonlanır:
1. **1. Pas:** Oyuncu A, kalan hücrelerin hiçbirini bilemez ve 30 saniye beklemek yerine "Pas" butonuna basar (veya süresi biter). Sıra Oyuncu B'ye geçer.
2. **Uyarı:** Oyuncu B'nin ekranında *"Rakip pas geçti. Eğer sen de pas geçersen oyun kilitlenir ve sona erer!"* uyarısı belirir.
3. **2. Pas:** Oyuncu B de doğru tahmin yapamaz ve "Pas" derse (veya süresi biterse) **Deadlock** gerçekleşir.
4. **Sonuçlandırma:** Oyun anında biter. Tıpkı tahta dolmuş gibi, o ana kadar tahtada **en çok hücresi olan** oyuncu kazanır. Eşitlik varsa beraberlik verilir. Oyun sonunda boş hücrelerin cevapları (öğreticilik) her iki oyuncuya da gösterilir.

## Kısıtlamalar ve Uç Durumlar (Edge Cases)

1. **Mükerrer Kullanım Engeli:** 
   - Takım Matrisinde: Bir futbolcu tahtada **yalnızca bir kez** kullanılabilir. Örneğin "Chelsea-Arsenal" kesişimine "Fabregas" yazıldıysa, tahtanın başka bir hücresindeki "Barcelona-Chelsea" kesişimine tekrar "Fabregas" yazılamaz.
   - Oyuncu Matrisinde: Bir takım tahtada **yalnızca bir kez** kullanılabilir.
2. **Kesişmeyen (İmkansız) Tahta Engeli:** Sistem 3x3 tahtayı oluştururken, başlıkları tamamen rastgele seçmez. Tahtadaki tüm 9 hücrenin de **kesinlikle en az bir doğru cevabı (futbolcu veya takım)** olmak zorundadır. Algoritma tahtayı oluştururken bu teyidi veritabanından yapmak zorundadır.
3. **Oluşturulan Başlıkların Farklılığı:** Satır ve sütunlarda aynı takım (veya oyuncu) yer alamaz. Yani 3 satır ve 3 sütun toplamda 6 benzersiz ögeden oluşmalıdır.

## Oynanış Akışı (UI/UX)
1. **Oyun Ekranı:** Merkezde 4x4 (aslında oynanabilir 3x3) büyük, şık ve okunabilir bir ızgara (grid) yer alır.
2. **Başlıklar:** En üstteki yatay şeritte 3 logo/portre (sütun başlıkları), en soldaki dikey şeritte 3 logo/portre (satır başlıkları) yer alır. Takım matrisinde kulüp logoları, oyuncu matrisinde oyuncu yüzleri kullanılır.
3. **Hücre Seçimi:** Kullanıcı boş bir hücreye dokunduğunda o hücre vurgulanır ve ekranın altında (veya modal olarak) arama çubuğu belirir. Kesişimdeki iki başlık görsel olarak bir araya getirilip kullanıcıya görevi hatırlatır (Örn: `[Chelsea Logosu] + [Arsenal Logosu]`).
4. **Animasyonlar:** Online modda rakip doğru tahmin yaptığında hücre rakibin rengiyle (örn: Kırmızı O) bir animasyonla dolarken, sizinki (örn: Mavi X) olarak dolar. Seriyi tamamlayan çizgi ekrana çarpıcı bir görsel efektle çizilir.
