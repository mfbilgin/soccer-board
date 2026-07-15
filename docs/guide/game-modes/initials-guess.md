# Baş Harflerinden Futbolcu Tahmini

Harf kısıtlamalarıyla hafızayı zorlayan, kelime türetme ve futbol bilgisini birleştiren spesifik bir mod.

## Online Mod Oynanışı
1. Maç başladığında sistem, her iki oyuncudan da rastgele **1'er harf** seçmesini ister (Örn: 1. Oyuncu **M**, 2. Oyuncu **A** seçer).
2. Sistem bu harfleri birleştirir. Kural şudur: **Soyadı (veya Bilinen Adı) 1. oyuncunun harfiyle (M) başlayıp, 2. oyuncunun harfiyle (A) biten** bir futbolcu bulmak.
3. *Örnek Cevap:* **M**aradon**a** veya **M**ortar**a**.
4. Her iki oyuncunun da tahmin yapabilmesi için **30 saniyesi** vardır.
5. Doğru oyuncuyu ilk yazan taraf turu kazanır. 30 saniye boyunca kimse bulamazsa o el berabere biter (kimse puan alamaz).

## Offline Mod Oynanışı
- Sistem kendisi rastgele 2 harf belirler (Örn: S ve O).
- Oyuncu, offline olarak sistemin belirlediği harflerle başlayan ve biten bir oyuncu bulmaya çalışır (Örn: **S**oriat**o**). Süre kısıtlaması olmadan pratik yapmak için idealdir.
