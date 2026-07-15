# Ana Ekran (Home Screen)

Kullanıcı giriş yaptıktan sonra uygulamanın merkezi olan `HomeScreen.js` ekranına yönlendirilir.

## Navigasyon ve İçerik
Ana ekran, kullanıcının profilini, ekonomisini ve tüm oyun modlarına giriş kapılarını barındırır.

1. **Üst Bar (Header / Profil Alanı):**
   - Kullanıcının Seviyesi (Level) ve XP çubuğu (Progress bar).
   - Sahip olduğu Çipler (Chips) ve Elmaslar (Gems).
2. **Orta Alan (Oyun Modları Vitrini):**
   - **Play TicTacToe:** Singleplayer TicTacToe moduna yönlendirir.
   - **Play Target Score:** Target Score moduna yönlendirir.
   - **Play Pyramid:** Piramit moduna yönlendirir.
   - **Multiplayer (Online):** Lobby ve Oda seçim ekranına götürür.
3. **Alt Bar (Tab Navigation):**
   - Home, Leaderboard, Friends, Profile sekmeleri arasında hızlı geçiş sağlar.

## Kullanıcı Akışı (User Flow)
Kullanıcı herhangi bir oyun moduna tıkladığında, eğer modu oynamak için yeterli Çip'i (Chip) yoksa ekranda "Yetersiz Bakiye" uyarısı çıkar. Yeterli çipi varsa, oyuna girer ve bakiyesinden giriş ücreti (Entry Fee) düşülür.
