# 2 Takım/Ülkeden Futbolcu Bul Modu — "Kesişim Düellosu"

Yalnızca Online olarak oynanabilen, yüksek hız ve bilgi gerektiren spesifik bir refleks modudur.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki tasarım GDD'den (§3.5) alınmıştır.
:::

## Modun Türleri
Oyun iki farklı versiyonda oynanabilir:

### 1. Takım & Ülke Modu
- Sistem bir tarafta bir **Kulüp Takımı**, diğer tarafta bir **Ülke (Milli Takım)** gösterir.
- *Örnek:* Real Madrid & Hırvatistan.
- *Amaç:* Kariyerinde Real Madrid forması giymiş, Hırvat uyruklu bir oyuncuyu (Örn: Luka Modric, Mateo Kovacic) **ilk söyleyen** (veya klavyeden ilk yazan) oyuncu maçı kazanır.

### 2. Takım & Takım Modu
- Sistem iki farklı **Kulüp Takımı** gösterir.
- *Örnek:* Juventus & Manchester United.
- *Amaç:* Her iki takımda da forma giymiş bir oyuncuyu (Örn: Paul Pogba, Cristiano Ronaldo) ilk tahmin eden taraf turu kazanır.

## Akış (Online, gerçek zamanlı)
1. Sistem iki kriteri gösterir: *"Brezilya + AC Milan."*
2. Her iki oyuncu da aynı anda tahmin etmeye çalışır (WebSocket üzerinden).
3. İlk geçerli/doğru cevabı gönderen kazanır.

## Hız ve Refleks
Soket üzerinden yapılan tahminler milisaniyeler içerisinde değerlendirilir. Yanlış tahmin kısa süreliğine yeni tahminde bulunmayı engelleyebilir (rastgele isim sallamayı önlemek için).

## Kısıtlamalar ve Uç Durumlar
- **Çözülebilirlik garantisi:** Sistem, kriterleri rastgele seçmeden önce en az bir geçerli cevabın var olduğunu veritabanından doğrulamalıdır (aksi halde çözümsüz bir tur çıkabilir).
- **Süre limiti:** Kimse doğru cevabı bulamazsa el berabere biter ve oda ücreti iade edilir (bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core) — ortak online kurallar).
- **Çoklu doğru cevap:** Kriterlere uyan birden fazla oyuncu olabilir; hangisi olursa olsun ilk geçerli cevap yeterlidir.

## Olası Backend İhtiyaçları (tasarım aşaması)
- Bir takım + bir ülke ya da iki takım seçip aralarında ortak oynamış en az bir oyuncu olduğunu `player_club_stats`/`player_national_stats` üzerinden doğrulayan bir üretim (`generate`) endpoint'i.
- Multiplayer WebSocket akışına (`routers/multiplayer.py`) yeni bir oyun modu olarak entegrasyon — mevcut TicTacToe/Target Score odalarıyla aynı oda/eşleştirme altyapısını kullanabilir.
