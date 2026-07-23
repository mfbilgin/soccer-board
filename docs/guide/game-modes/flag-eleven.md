# Bayraklarla Kurulu İlk 11 Modu — "Bayrak XI"

Görsel hafıza ve coğrafya bilgisinin futbolla harmanlandığı, oyunculara sadece "uyruklar" üzerinden ipucu verilen bir moddur.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki tasarım GDD'den (§3.9) alınmıştır.
:::

## Oyun Mantığı
- Ekranda bir futbol sahası belirir ve üzerinde klasik bir diziliş (Örn: 4-3-3) vardır.
- Sistem gizli bir takımın (Örn: 2010 Inter Milan) ilk 11'ini sahaya dizer ancak oyuncuların **isimlerini ve yüzlerini gizler**.
- Sadece o mevkideki oyuncunun **uyruğunun bayrağı** gösterilir (Kalede Brezilya bayrağı, sağ bekte Arjantin bayrağı, forvette Arjantin bayrağı vb.).

## Kurallar
- Kullanıcı sadece bayraklara bakarak o kadronun "Hangi Kulüp (ve hangi yıl)" olduğunu veya kadrodaki spesifik futbolcuları bulmaya çalışır.
- **Offline Mod:** Kullanıcının, bu bayrak dizilişindeki takımı bulmak için toplam **3 hakkı** vardır.
- **Online Mod:** İki oyuncu aynı sahayı görür. Doğru takımı sisteme giren **ilk oyuncu** kazanır; burada da her iki tarafın maksimum **3 tahmin hakkı** vardır (rastgele takım sallamayı engellemek için).

## Kısıtlamalar ve Uç Durumlar
- **Aynı uyruktan birden çok oyuncu:** Örneğin ilk 11'in tamamı aynı milletten ise ipucu zayıflar; bu tür kadrolar sistemde otomatik olarak daha zor (daha az kullanılan) olarak işaretlenmelidir.
- **Hangi tarih/maç?** Belirli bir ikonik kadro veya döneme ait diziliş seçilir (örn. "şampiyonluk finali XI"); rastgele herhangi bir sezon değil, bilinirliği yüksek kadrolar tercih edilmelidir.
- **Çift uyruklu oyuncular:** Birincil uyruk veya fiilen temsil ettiği milli takım esas alınır (örn. bir oyuncu hem İspanyol hem Faslı olabilir ama Fas milli takımını temsil ediyorsa bayrak Fas olmalıdır).
- **Tahmin biçimi:** Ya doğrudan takım adı tahmin edilir, ya da kademeli olarak kadrodaki oyuncu isimleri tek tek tahmin ettirilebilir *(Tasarım Kararı — ikisi de değerlendirilebilir)*.

## Olası Backend İhtiyaçları (tasarım aşaması)
- Belirli, önceden küratörlüğü yapılmış "ikonik kadro" verisi (11 oyuncu + mevki + o dönemki takım) tutan yeni bir tablo — mevcut `player_club_stats` tablosu sezon bazlı istatistik tutuyor ama "belirli bir maçın ilk 11'i" bilgisini tutmuyor, bu nedenle bu mod için ek veri toplama/küratörlük gerekir.
- `players.nationality` alanı zaten mevcut (bkz. [Database Structure](/guide/database)), bayrak gösterimi için yeterli.
