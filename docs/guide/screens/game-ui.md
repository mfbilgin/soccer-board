# Oyun İçi Ekranlar (Game UI)

Bu bölüm, kullanıcının aktif olarak oyun oynadığı ve oyun sonuçlarını gördüğü ekranları kapsar.

## TicTacToeScreen.js
- 3x3 bir grid (ızgara) barındırır.
- Satır ve sütun başlıklarında (Header) kulüp logoları, ülke bayrakları veya istatistik ikonları yer alır.
- **Hamle Akışı:** Oyuncu boş bir kutuya tıklar -> Arama (Search) modalı açılır -> Arama barına oyuncu ismi yazar -> API'den gelen öneri listesinden doğru oyuncuyu seçer -> Yanıt backend'e gider -> Doğruysa yeşil tik (X/O ikonu) konur.

## TargetScoreResultScreen.js
Oyun bittikten sonra çıkan "Maç Sonu" ekranıdır.
- Oyuncunun kaç tahminde hedef puana ulaştığı, harcadığı süre ve jokerler gösterilir.
- "Kazanılan XP: +150" veya "Kazanılan Çip: +20" gibi oyun içi ödüllerin animasyonlu bir şekilde sayacı artırarak ekrana yansıdığı, oyuncuyu tatmin eden ödül ekranıdır.
- "Play Again" (Tekrar Oyna) veya "Back to Home" (Ana Ekrana Dön) butonları bulunur.
