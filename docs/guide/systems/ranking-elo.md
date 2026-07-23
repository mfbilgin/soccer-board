# Rank ve ELO Sistemi

Oyundaki asıl rekabeti tetikleyen, oyuncuları yetenek ve bilgi düzeylerine göre birbirleriyle eşleştiren sıralama sistemidir.

## Başlangıç ve ELO Mantığı
- **Başlangıç:** Sisteme kayıt olan her yeni oyuncu **100 Rating** puanı ile oyuna başlar.
- **Kazanç/Kayıp:** Yalnızca online maçlarda geçerlidir. Standart Elo formülü **K=32** sabitiyle uygulanır:
  - `expected_winner = 1 / (1 + 10^((loser.rating - winner.rating) / 400))`
  - `winner.rating += K * (1 - expected_winner)`, `loser.rating += K * (0 - expected_loser)` (yani kaybeden puan kaybeder).
  - Güçlü bir rakibi yenmek daha çok puan kazandırır, standart satranç Elo mantığıdır.
- **Eşleştirmede kullanımı:** [Multiplayer Core](/guide/game-modes/multiplayer-core)'daki eşleştirme, oda + rating yakınlığına göre yapılır; bekleme süresi uzadıkça tolerans genişler.

## Ligler ve Haftalık Sıfırlama

*Durum: kodlanmadı. Yalnızca ham `rating` sayısı vardır, kümeleme aşağıdaki tasarıma göre henüz uygulanmamıştır.*

Sistem, oyuncuları sahip oldukları rating'e göre şu kümelere ayıracak şekilde tasarlanmıştır:

| Küme | Rating Aralığı |
|---|---|
| Bronz Lig (Amatör) | 0 - 119 |
| Gümüş Lig (Yarı-Profesyonel) | 120 - 149 |
| Altın Lig (Profesyonel) | 150 - 189 |
| Elit Lig (Dünya Klası) | 190 - 249 |
| Efsane Ligi | 250+ |

- Sistem **her Pazar 23:59 (sunucu saati)** ligleri yeniden hesaplar.
- Haftayı kendi liginde **1. sırada** bitiren oyuncuya otomatik **10 Gems** ödülü verilir (bkz. [Gems & Chips](/guide/systems/economy-gems-chips)).
- Sezon (haftalık ligden ayrı, aylık bir üst döngü) kavramı bu sürümde yoktur — yalnızca haftalık sıfırlama vardır.

**Backend Sözleşmesi:**
- `GET /api/social/leaderboard/global` zaten `rating`'e göre ilk 50'yi döner (bkz. [Social & Leaderboards](/guide/systems/social-leaderboards)) — lig kümeleme bunun üzerine, sorgu anında `rating` aralığına göre hesaplanarak eklenebilir, ayrı bir tabloya gerek yoktur.
- Haftalık ödül dağıtımı için, Pazar gecesi çalışan bağımsız bir zamanlanmış görev (scraper'dan ayrı, örn. `backend/weekly_league_rewards.py`) yazılması gerekir.
