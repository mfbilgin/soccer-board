# Oyuncular-Takımlar Örgüsü Modu — "Zincir Oyunu"

**2 ila 6 kişinin** aynı lobide oynayabildiği, "Kelime Zinciri" oyununun futbol dünyasına uyarlanmış, hızlı ve eğlenceli bir eleme modudur.

::: danger Henüz kodlanmadı
Bu mod için backend'de router, frontend'de ekran yok. Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir. Yalnızca online (gerçek zamanlı çok oyunculu) olarak tasarlanmıştır. [Multiplayer Core](/guide/game-modes/multiplayer-core)'daki 1v1 eşleştirme/kazanan-kaybeden mantığı bu N-kişilik moda **uygun değildir** — aşağıdaki spec kendi bağımsız lobi/skor mantığını tanımlar.
:::

## Oyun Akışı
Oyun sırayla ilerler. Zincir her zaman "Oyuncu → Takım → Oyuncu → Takım" şeklinde devam etmek zorundadır.

1. Sistem ilk oyuncuyu ve rastgele bir başlangıç futbolcusunu seçer: **"Lionel Messi"** (lobiye "zincir buradan başlıyor" olarak gösterilir, ilk sıradaki oyuncudan devam etmesi istenir).
2. Sıra 2. oyuncuya geçer. Bu oyuncunun, Messi'nin kariyerinde oynadığı bir takımı söylemesi zorunludur. Cevap verir: **"Barcelona"**
3. Sıra bir sonraki (hayatta kalan) oyuncuya geçer. Bu oyuncunun, Barcelona'da forma giymiş (daha önce söylenmemiş) başka bir oyuncuyu söylemesi gerekir: **"Ronaldinho"**
4. Sıra bir sonrakine geçer: Ronaldinho'nun oynadığı başka bir takım söylenmelidir: **"AC Milan"**
5. Bu döngü, masada **son 1 kişi** kalana kadar devam eder.

## Eleme ve Süre Kuralları
- **Tekrar Kuralı:** O maç içinde daha önce söylenmiş bir oyuncu veya takım tekrar söylenemez. Backend, oda başına bir `used_ids: {player_ids: set, team_ids: set}` listesi tutar.
- **Süre Sınırı:** Sıra size geldiğinde cevap vermek için **15 saniye** vardır (sunucu taraflı, [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki 30 saniyelik turn-timer deseniyle aynı mimaride, süresi farklı).
- 15 saniye içinde doğru, kurallara uyan ve daha önce söylenmemiş bir cevap veremeyen oyuncu **elenir** ve izleyici moduna geçer.
- **Son 1 kişi** kalana kadar oyun devam eder; kalan kişi turun galibi olur.

## Matematiksel Çıkmaz (dead-end) Kuralı — kesin çözüm
Bir düğümün (oyuncu/takım) tüm geçerli devamları veritabanı seviyesinde tükenmiş olabilir (örn. seçilen oyuncu yalnızca zaten kullanılmış takımlarda oynamış). Bu, bir insanın bilgi eksikliğinden **farklıdır** ve 15 saniyelik eleme kuralıyla karıştırılmaz:
- Bir oyuncu doğru cevap verdiğinde, backend o cevabın yeni düğümünün (`used_ids` hariç) **en az bir geçerli devamı** olup olmadığını hemen kontrol eder.
- Eğer sıfırsa: kimse elenmez. Lobiye *"Zincir tıkandı, yeni zincir başlıyor!"* mesajı gösterilir, backend **yeni bir rastgele başlangıç futbolcusu** seçer (kullanılmamış bir oyuncudan), `used_ids` sıfırlanır, sıra bir sonraki hayatta kalan oyuncudan devam eder. Bu bir "round" sonu değildir, oyun durumu (kim elendi, kimin sırası kimden sonra geliyor) korunur.

## Kısıtlamalar ve Uç Durumlar
- **Geçerlilik doğrulaması:** Söylenen oyuncunun gerçekten o takımda oynayıp oynamadığı `player_club_stats` (kulüp) veya `player_national_stats`+`player_transfers` (kesin geçmiş) üzerinden anında doğrulanır.
- **Tekrar kontrolü:** `used_ids` sunucuda tutulur, istemciye güvenilmez.
- **İtiraz mekanizması gerekmez:** Sistem otoritedir — cevap veritabanına göre doğru/yanlış kabul edilir.
- **Lobi boyutu:** Minimum 2, maksimum 6 oyuncu. 6'dan fazla katılım isteği reddedilir (oda dolu).
- **Berabere biten senaryo yoktur:** Eleme oyunu olduğu için her zaman tam olarak 1 kazanan kalır (2 kişilik bir lobide bile, biri elenene kadar devam eder).

## Backend İhtiyaçları (uygulanacak API/WebSocket sözleşmesi)
- `multiplayer.py`'ye N-kişilik lobi destekleyen yeni bir oda tipi: `game_mode: "chain_reaction"`, `room.players` mevcut `Dict[str, WebSocket]` yapısı zaten N kişiyi destekler (2 kişiyle sınırlı değildir), ama `award_winnings`/`update_rating` gibi ikili (winner/loser) fonksiyonlar bu mod için **kullanılmaz** — tek kazanana tüm havuzu veren, kalan herkesi "kaybeden" sayan yeni bir `award_chain_winner(db, winner_id, total_pool, all_loser_ids)` fonksiyonu yazılması gerekir.
- WebSocket action `chain_answer`: `{"entity_id": ..., "entity_type": "player"|"team"}`; sırası gelmeyen oyuncudan gelen istekler yok sayılır (TicTacToe'daki `active_player` kontrolüyle aynı desen).
- Elenen oyuncuların `websocket` bağlantısı kapatılmaz, `role: "spectator"` olarak işaretlenip yayın almaya devam eder.
