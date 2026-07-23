# Oyuncular-Takımlar Örgüsü Modu — "Zincir Oyunu"

**2 ila 6 kişinin** aynı lobide oynayabildiği, "Kelime Zinciri" oyununun futbol dünyasına uyarlanmış, hızlı ve eğlenceli bir eleme modudur.

**Durum:** Kodlandı ve çalışıyor. Yalnızca online (gerçek zamanlı çok oyunculu) olarak tasarlanmıştır. [Multiplayer Core](/guide/game-modes/multiplayer-core)'daki 1v1 eşleştirme/kazanan-kaybeden mantığı bu N-kişilik moda uygun olmadığı için kendi bağımsız lobi/skor mantığı vardır (`socket_manager.py`'deki `join_chain_lobby`, `routers/multiplayer.py`'deki `chain_*` fonksiyonları, `chain_reaction.py`'deki `ChainReactionEngine`).

Kod karşılığı: `backend/socket_manager.py` (N-kişilik lobi), `backend/routers/multiplayer.py` (`chain_lobby_countdown`, `start_chain_reaction_game`, `chain_answer` WS action'ı), `backend/chain_reaction.py` (zincir motoru — `tictactoe.py`'nin takım/oyuncu önbelleğini yeniden kullanır), `frontend/screens/multiplayer/ChainReactionScreen.js`.

## Oyun Akışı
Oyun sırayla ilerler. Zincir her zaman "Oyuncu → Takım → Oyuncu → Takım" şeklinde devam etmek zorundadır.

1. Sistem ilk oyuncuyu ve rastgele bir başlangıç futbolcusunu seçer: **"Lionel Messi"** (lobiye "zincir buradan başlıyor" olarak gösterilir, ilk sıradaki oyuncudan devam etmesi istenir).
2. Sıra 2. oyuncuya geçer. Bu oyuncunun, Messi'nin kariyerinde oynadığı bir takımı söylemesi zorunludur. Cevap verir: **"Barcelona"**
3. Sıra bir sonraki (hayatta kalan) oyuncuya geçer. Bu oyuncunun, Barcelona'da forma giymiş (daha önce söylenmemiş) başka bir oyuncuyu söylemesi gerekir: **"Ronaldinho"**
4. Sıra bir sonrakine geçer: Ronaldinho'nun oynadığı başka bir takım söylenmelidir: **"AC Milan"**
5. Bu döngü, masada **son 1 kişi** kalana kadar devam eder.

## Eleme ve Süre Kuralları
- **Tekrar Kuralı:** O maç içinde daha önce söylenmiş bir oyuncu veya takım tekrar söylenemez. Oda başına söylenmiş oyuncu/takım ID'lerinin bir listesi tutulur.
- **Süre Sınırı:** Sıra size geldiğinde cevap vermek için **15 saniye** vardır ([TicTacToe](/guide/game-modes/tictactoe-4x4)'daki turn-timer deseniyle aynı mimaride, süresi farklı).
- 15 saniye içinde doğru, kurallara uyan ve daha önce söylenmemiş bir cevap veremeyen oyuncu **elenir** ve izleyici moduna geçer.
- **Son 1 kişi** kalana kadar oyun devam eder; kalan kişi turun galibi olur.

## Matematiksel Çıkmaz (dead-end) Kuralı
Bir düğümün (oyuncu/takım) tüm geçerli devamları veritabanı seviyesinde tükenmiş olabilir (örn. seçilen oyuncu yalnızca zaten kullanılmış takımlarda oynamış). Bu, bir insanın bilgi eksikliğinden farklıdır ve 15 saniyelik eleme kuralıyla karıştırılmaz:
- Bir oyuncu doğru cevap verdiğinde, sistem o cevabın yeni düğümünün (kullanılmışlar hariç) en az bir geçerli devamı olup olmadığını hemen kontrol eder.
- Eğer sıfırsa: kimse elenmez. Lobiye *"Zincir tıkandı, yeni zincir başlıyor!"* mesajı gösterilir, sistem **yeni bir rastgele başlangıç futbolcusu** seçer (kullanılmamış bir oyuncudan), kullanılmışlar listesi sıfırlanır, sıra bir sonraki hayatta kalan oyuncudan devam eder. Bu bir "round" sonu değildir, oyun durumu (kim elendi, kimin sırası kimden sonra geliyor) korunur.

## Kısıtlamalar ve Uç Durumlar
- **Geçerlilik doğrulaması:** Söylenen oyuncunun gerçekten o takımda oynayıp oynamadığı kariyer verileri üzerinden anında doğrulanır.
- **Tekrar kontrolü:** Kullanılmışlar listesi sunucuda tutulur, istemciye güvenilmez.
- **İtiraz mekanizması gerekmez:** Sistem otoritedir — cevap veritabanına göre doğru/yanlış kabul edilir.
- **Lobi boyutu:** Minimum 2, maksimum 6 oyuncu. 6'dan fazla katılım isteği reddedilir (oda dolu).
- **Berabere biten senaryo yoktur:** Eleme oyunu olduğu için her zaman tam olarak 1 kazanan kalır (2 kişilik bir lobide bile, biri elenene kadar devam eder).

## Backend Sözleşmesi
- Multiplayer oda yapısı N-kişilik lobiyi zaten destekler (oyuncu koleksiyonu sabit ikiyle sınırlı değildir); yeni bir oda tipi: `game_mode: "chain_reaction"`. Standart ikili (kazanan/kaybeden) ödül fonksiyonları bu mod için kullanılmaz — tek kazanana tüm havuzu veren, kalan herkesi kaybeden sayan ayrı bir ödül fonksiyonu yazılması gerekir.
- WebSocket action `chain_answer`: `{"entity_id": ..., "entity_type": "player"|"team"}`; sırası gelmeyen oyuncudan gelen istekler yok sayılır.
- Elenen oyuncuların bağlantısı kapatılmaz, `role: "spectator"` olarak işaretlenip yayın almaya devam eder.
