# İstatistik Hedefleri Modu (Stats Target)

Bu mod, kullanıcının belirli bir ligde ve kısıtlı sayıda oyuncuyla verilen istatistik hedefini tutturmaya çalıştığı bir futbol bulmacasıdır. **Amaç hedefi aşmak değil, hedefe tam olarak (ya da olabildiğince yakın) ulaşmaktır.**

## Oyun Amacı
Oyuncu, sistem tarafından verilen **Lig (lg)** bazında, yine sistemin belirlediği **Oyuncu Sayısı (pa)** hakkını kullanarak, hedeflenen **İstatistik (tar)** için istenen **Hedef Sayıya (ta)** en yakın sonucu elde etmeye çalışır.

## Soru Kısıtları ve Algoritması

Sistemin kullanıcının karşısına çıkaracağı bulmaca aşağıdaki kesin kurallara göre oluşturulur:

1. **İzin Verilen Ligler (lg):** Yalnızca Avrupa'nın 5 büyük ligi, Türkiye Süper Lig (TR1) ve Milli Maçlar arasından seçilir.
2. **Hedef Futbolcu Sayısı (pa):** Yalnızca **3** ya da **5** olabilir.
3. **Verilen Görev (tar):** Aşağıdaki metriklerden biri olabilir:
   - Gol Sayısı (`goals`)
   - Maç Sayısı (`appearances`)
   - Toplam Oynanan Dakika (`minutes_played`)
   - Asist Sayısı (`assists`)
   - Sarı Kart Sayısı (`yellow_cards`)
   - Kırmızı Kart Sayısı (`red_cards`)
4. **Hedef Miktarı (ta) Belirleme Algoritması:**
   - Backend sistemi, seçilen kriterleri tam olarak sağlayan `pa` (3 veya 5) sayıda rastgele aktif/emekli süperstar oyuncu seçer.
   - Bu oyuncuların `tar` cinsinden istatistiklerini toplar.
   - Çıkan sonucu yukarı doğru düz (ondalık) bir sayıya yuvarlar. (Örn: Çıkan toplam 271 ise, hedef `ta = 300` olarak belirlenir).

## Puanlama ve Kazanma Koşulları (Kritik)

Oyunun temel zorluğu hedefi geçmekte değil, **nokta atışı hedefe yaklaşmaktadır**. Seçtiğiniz oyuncuların toplamı hedeften az ya da çok olabilir, önemli olan aradaki matematiksel farktır.

**Singleplayer (Tek Oyunculu) Puanlaması:**
Kullanıcı tüm kutuları doldurup tahmini gönderdiğinde çıkan sonuç hedefe (ta) göre yüzdelik olarak değerlendirilir:
- **%1 ± Yakınlık:** Kusursuz tahmin! **25 XP** kazandırır.
- **%10 ± Yakınlık:** Başarılı tahmin. **10 XP** kazandırır.
- **Daha Fazla Sapma:** Zayıf tahmin. Sadece teselli puanı olan **5 XP** kazandırır.

**Multiplayer (Online) Akışı ve Kazanma Koşulu:**
Online mod, iki oyuncunun aynı anda aynı bulmacayı çözdüğü, sürenin ve heyecanın ön planda olduğu rekabetçi bir yapıdadır (WebSockets ile anlık çalışır).
1. **Oda ve Eşleşme:** İki oyuncu eşleşir ve her ikisinin ekranına aynı anda aynı bulmaca (Aynı hedef, aynı lig) düşer.
2. **Süre (Timer):** Oyunun 60 veya 90 saniyelik katı bir süresi vardır. Süre baskısı oyuncuları hızlı düşünmeye iter.
3. **Rakibi Görme:** Oyuncular rakibin kutularının dolduğunu anlık olarak görür (Örn: "Rakip 1. kutuyu doldurdu!"), ancak hangi oyuncuyu seçtiğini **göremez**. Bu durum büyük bir heyecan ve panik yaratır.
4. **Kilitleme (Bitir):** Bir oyuncu seçimlerini bitirip "Bitir" butonuna bastığında tahminini kilitler. Diğer oyuncu süresi bitene kadar (veya o da Bitir diyene kadar) seçime devam edebilir.
5. **Showdown (Sonuç Ekranı):** İki oyuncu da kilitlediğinde veya süre bittiğinde ekran ikiye bölünür. Oyuncuların seçtiği futbolcular ve toplam skorları aynı anda açığa çıkar.
6. **Kazanma ve Eşitlik (Tie-Breaker):** Toplam skoru hedefe (ta) **en yakın olan** maçı kazanır. Eğer her iki oyuncu da hedefe *tamamen aynı uzaklıktaysa*, tahmini **ilk kilitleyen (Süreyi daha hızlı kullanan)** oyuncu galip sayılır. Boş kutu bırakan oyuncu direkt kaybeder.

## Kısıtlamalar ve Uç Durumlar (Edge Cases)
Bu oyun modunda hile yapılmasını veya oyunun mantığının kırılmasını önlemek için aşağıdaki kurallar uygulanır:
1. **Mükerrer Oyuncu Engeli:** Bir oyuncu birden fazla kutuya yerleştirilemez.
2. **Geçersiz Oyuncu Uyarısı (Dummy Engeli):** Kullanıcının o ligde hiç oynamamış veya istenen istatistikte değeri "0" olan bir oyuncuyu (Örn: Hedef Premier Lig iken kutulardan birine Neymar'ı seçmesi) seçmesi durumunda sistem oyuncuyu kutuya yerleştirmez. Ekranda "Bu oyuncu bu ligde hiç oynamadı, başka bir tahmin yapın." şeklinde bir uyarı çıkar. Bu sayede hem kullanıcının bilmeden ceza alması engellenir, hem de "3 oyuncu" şartını 1 oyuncuyla bypass etme açığı tamamen kapatılmış olur.
3. **Arama Çubuğu Şeffaflığı:** Arama kısmı (Autocomplete) filtreleme yapmaz; dünyadaki tüm oyuncuları getirir. Kullanıcı kimin o ligde oynadığını kendisi bilmek zorundadır.

## Oynanış Akışı (UI/UX)
Mevcut kod altyapımız (`TargetScoreScreen.js`) üzerinden ilerlenecektir:
1. **Ekran Yerleşimi:** Oyuncu modu seçtiğinde sayfanın en üstünde seçilmiş lig ve alt kısmında hedef skor yazar (Örn: "Premier League - Toplam 300 Gol").
2. **Oyuncu Barları (Slotlar):** Hedefin hemen altında `pa` (3 veya 5) kadar **boş oyuncu barı** yer alır.
3. **Arama ve Seçim:** Oyuncu boş bir bara tıkladığında standart `SearchModal` (Arama Kutusu) açılır. Kullanıcı klavyeden oyuncu ismini yazmaya başladığında mevcut sistemdeki gibi futbolcular listelenir.
4. **Doğrulama ve Sonuç:** Tüm kutular (`pa` adet) doldurulduktan sonra "Bitir" butonuna basılır. Sistem, API (`/validate`) üzerinden seçilen oyuncuların geçerliliğini ve gerçek skorlarını toplar, hedefe olan yakınlık yüzdesine göre kazanılan XP'yi hesaplayıp ekranda gösterir.
