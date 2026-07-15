# 4x4 TicTacToe Modu

Football TicTacToe'nun standart versiyonundan farklı olarak, 4 satır ve 4 sütunla oynanan, çapraz geçişleri ve kesişim mekanikleri çok daha karmaşık olan amiral gemisi modudur.

## Oyun Türleri (Kesişim Kuralları)
Bu mod iki farklı matris tasarımıyla oynanabilir:

### 1. Takım-Takım Kesişimi (Klasik)
- **1. Satır ve 1. Sütun:** Dünyaca ünlü futbol kulüpleri ve milli takımlardan oluşur.
- **Amaç:** Kullanıcı, iki takımın kesiştiği hücreye, kariyeri boyunca **her iki takımda da forma giymiş** bir futbolcunun ismini yazar.
- *Örnek:* Satırda Barcelona, sütunda PSG var ise hücreye "Neymar" veya "Lionel Messi" yazılabilir.

### 2. Oyuncu-Oyuncu Kesişimi (Ters TicTacToe)
- **1. Satır ve 1. Sütun:** Belli başlı ünlü futbolculardan oluşur.
- **Amaç:** Kullanıcı, iki oyuncunun kesiştiği hücreye, bu iki futbolcunun kariyerlerinde **ortak olarak oynadıkları (aynı anda olmak zorunda değil, aynı kulüp/milli takım forması giymiş olmaları yeterli) bir takımın** ismini yazar.
- *Örnek:* Satırda Cristiano Ronaldo, sütunda Karim Benzema var ise hücreye "Real Madrid" yazılabilir.

## Online ve Offline Oynanış
- **Online Mod:** İki oyuncu aynı anda 4x4 grid üzerinde oynar. Hamle süresi kısıtlıdır. 4 hücreyi dikey, yatay veya çapraz tamamlayan kazanır.
- **Offline Mod:** Oyuncu süre baskısı olmadan tüm tahtayı kendi başına (veya minimum hatayla) tamamlamaya çalışır.
