# En 'X' Kadroyu Kur Modu (Extreme Squad)

Bu mod, oyuncunun güncel futbol kadrolarındaki futbolcuların fiziksel ve demografik özelliklerine (Yaş, Boy) ne kadar hakim olduğunu ölçen bir kadro mühendisliği oyunudur.

## Oyun Amacı ve Hedef
Sistem oyuncudan belirli bir fiziksel veya demografik özelliğe odaklanarak bir kadro (Örn: 11 kişi veya 5 kişi) kurmasını ister. 
- **Örnek Görev 1:** *"Aşağıdaki takımların aktif oyuncularını kullanarak kurabileceğin EN GENÇ kadroyu kur."*
- **Örnek Görev 2:** *"Aşağıdaki takımların aktif oyuncularını kullanarak kurabileceğin EN UZUN BOYLU kadroyu kur."*

## Kısıtlar ve Oynanış Kuralları
1. **Sistemin Takım Dayatması:** Oyuncu kendi kafasına göre herhangi bir takımdan oyuncu seçemez. Sistem, ekrandaki her bir pozisyon (slot) için bir takım belirler.
   - *Örnek Ekran:* 
     - 1. Slot: Milan (Kullanıcı Milan'ın güncel kadrosundan en genç oyuncuyu bulmaya çalışır)
     - 2. Slot: Real Madrid
     - 3. Slot: Fenerbahçe
2. **Aktiflik Şartı:** Seçilen futbolcu, istenen takımda **şu an aktif olarak** forma giyiyor olmalıdır (Geçmişte oynamış emekli veya transfer olmuş oyuncular kabul edilmez).
3. **Zaman Sınırı:** Kullanıcı belirlenen süre içinde (Örn: 90 Saniye) tüm slotları doldurmak zorundadır.

## Puanlama ve Kazanma Koşulları
Oyunun temel amacı, hedef metriğin (Toplam Yaş veya Toplam Boy) matematiksel olarak en uç noktasında kalmaktır.

**Singleplayer (Tek Oyunculu) Puanlaması:**
Kullanıcı tüm kadroyu kilitlediğinde, sistem kullanıcının kurduğu kadronun toplam yaşını/boyunu, *o takımlarla kurulabilecek teorik en mükemmel kadronun* (Absolute Best) toplamıyla kıyaslar.
- **Teorik En İyiye %1 - %5 Yakınlık:** Kusursuz (Örn: En uzun boylu kadro sınırı 21.50 metreydi, oyuncu 21.20 metre kurdu) -> **25 XP**
- **Teorik En İyiye %5 - %15 Yakınlık:** Başarılı -> **10 XP**
- **Daha Düşük Oran:** Zayıf -> **5 XP**

**Multiplayer (Online) Kazanma Koşulu:**
- **Aynı Anda Oynanış:** İki oyuncu eşleştiğinde ikisinin de ekranına aynı "Hedef" ve aynı "Takım Slotları" gelir. İki oyuncu da 90 saniye içinde kendi kadrosunu doldurmaya çalışır.
- **Rakibi Görme:** Rakibin hangi takıma oyuncu kilitlediği görülür ancak kimi kilitlediği görülmez (Kör Seçim).
- **Kazanma:** Süre bittiğinde veya iki oyuncu da kilitlediğinde ekran ortadan ikiye ayrılır (Showdown). Hedefe daha çok yaklaşan (Daha genç veya daha uzun kadroyu kuran) maçı kazanır.
- **Eşitlik Bozucu (Tie-Breaker):** Eğer iki oyuncu da milimetrik/günlük olarak aynı yaşta veya aynı boyda bir kadro kurmuşsa, kadrosunu **daha hızlı kilitleyen** galip gelir. Geçersiz (Aktif olmayan) oyuncu koyan veya boş bırakan direkt kaybeder.

## Veritabanı ve Backend Akışı
1. **Görev Üretimi:** Backend, `teams` tablosundan rastgele 5 veya 11 takım seçer. `players` tablosunda `is_active = True` olan ve son transfer verisi bu takımlarda olan oyuncuların `date_of_birth` veya `height` verilerini analiz edip "Teorik En İyi Skoru" hesaplar.
2. **Doğrulama (Validation):** Kullanıcı bir seçim yaptığında, backend oyuncunun şu an o takımda oynayıp oynamadığını kontrol eder.
3. **API Endpoints:**
   - `GET /api/games/extreme-squad/generate`: Yeni rastgele takımlar ve hedef verir.
   - `POST /api/games/extreme-squad/validate`: Kullanıcının oluşturduğu kadronun geçerliliğini ve toplam skorunu döner.
