# Baş Harflerinden Futbolcu Tahmini — "Harf Düellosu"

Harf kısıtlamalarıyla hafızayı zorlayan, kelime türetme ve futbol bilgisini birleştiren spesifik bir mod.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki tasarım GDD'den (§3.8) alınmıştır.
:::

## Tanım
Soyadı (veya bilinen adı) belirli bir **harfle başlayıp** belirli bir **harfle biten** bir futbolcuyu ilk söyleyen/yazan kazanır.

## Online Mod Oynanışı
1. Maç başladığında sistem, her iki oyuncudan da rastgele **1'er harf** seçmesini ister (Örn: 1. Oyuncu **M**, 2. Oyuncu **A** seçer).
2. Sistem bu harfleri birleştirir. Kural şudur: **Soyadı 1. oyuncunun harfiyle (M) başlayıp, 2. oyuncunun harfiyle (A) biten** bir futbolcu bulmak.
3. *Örnek Cevap:* **M**aradon**a** veya **M**ortar**a**.
4. Her iki oyuncunun da tahmin yapabilmesi için **30 saniyesi** vardır.
5. Doğru oyuncuyu ilk yazan taraf turu kazanır. 30 saniye boyunca kimse bulamazsa o el berabere biter (oda ücreti iade edilir, kimse puan alamaz).

## Offline Mod Oynanışı
- Sistem kendisi rastgele 2 harf belirler (Örn: S ve O).
- Oyuncu, sistemin belirlediği harflerle başlayan ve biten bir oyuncu bulmaya çalışır (Örn: **S**oriat**o**). Süre kısıtlaması yoktur, pratik yapmak için idealdir.

## Kısıtlamalar ve Uç Durumlar
- **Çözülebilirlik:** Kullanıcıların online modda kendi seçtiği harf çiftleri **imkânsız bir kombinasyon** oluşturabilir (o harflerle başlayıp biten hiçbir oyuncu olmayabilir). *(Tasarım Kararı: sistem harfler seçildikten sonra çözüm olup olmadığını kontrol eder; çözüm yoksa beraberlik/yeni tur başlatılır, veya kullanıcılar en baştan yalnızca "çözümü olan" harf havuzundan seçim yapar.)*
- **Soyadı vs. tam ad:** Bazı oyuncular tek isimle bilinir (Ronaldinho, Neymar). Veritabanındaki "sıralama adı / soyadı" (`known_as`) alanı esas alınır; hem tam isim hem bilinen isim kabul edilebilir.
- **Transkripsiyon:** Türkçe (İ/ı, ş, ç) ve diğer uluslararası karakterlerin normalizasyonu gerekir — aksi halde doğru cevap "yanlış yazım" yüzünden reddedilebilir.

## Olası Backend İhtiyaçları (tasarım aşaması)
- Harf çifti verildiğinde `players.known_as` üzerinde `LIKE 'X%Y'` tarzı bir sorgu ile en az bir eşleşme olduğunu doğrulayan bir kontrol endpoint'i.
- Girilen cevabın gerçekten o harf çiftine uyduğunu ve veritabanında var olduğunu doğrulayan bir `verify` endpoint'i.
