# Rank ve ELO Sistemi

Oyundaki asıl rekabeti tetikleyen, oyuncuları yetenek ve bilgi düzeylerine göre birbirleriyle eşleştiren sıralama sistemidir.

## Başlangıç ve ELO Mantığı (kodlanmış, çalışır durumda)
- **Başlangıç:** Sisteme kayıt olan her yeni oyuncu **100 Rating** puanı ile oyuna başlar (`models.User.rating = Column(Integer, default=100)`).
- **Kazanç/Kayıp:** Yalnızca online maçlarda geçerlidir. `services/economy.py`'deki `update_rating(db, winner_id, loser_id)`, standart Elo formülünü **K=32** sabitiyle uygular:
  - `expected_winner = 1 / (1 + 10^((loser.rating - winner.rating) / 400))`
  - `winner.rating += K * (1 - expected_winner)`, `loser.rating += K * (0 - expected_loser)` (yani kaybeden puan kaybeder).
  - Güçlü bir rakibi yenmek daha çok puan kazandırır, standart satranç Elo mantığıdır.
- **Eşleştirmede kullanımı:** [Multiplayer Core](/guide/game-modes/multiplayer-core)'daki eşleştirme, oda + rating yakınlığına göre yapılır; bekleme süresi uzadıkça tolerans genişler.

## Ligler ve Haftalık Sıfırlama

::: danger Kodlanmadı
`models.py`'de lig/küme (tier) ile ilgili bir tablo yoktur; haftalık sıfırlama işini yapacak bir zamanlanmış görev (cron/scheduler) de yoktur. Yalnızca ham `User.rating` sayısı vardır, kümeleme UI/backend'de **hesaplanmaz**. Aşağıdaki tasarım, kesinleştirilmiş ama henüz uygulanmamış bir spec'tir.
:::

Sistem, oyuncuları sahip oldukları rating'e göre şu **kesin** kümelere ayıracak şekilde tasarlanmıştır (bu sınırlar `models.User.rating`'in gerçek aralığına, yani 100 başlangıçlı Elo'ya göre kalibre edilmiştir — [roadmap taslağındaki](/guide/systems/economy-gems-chips) 1000-başlangıçlı sınırlar bu doküman için **geçersizdir**, çünkü kod 100'den başlıyor):

| Küme | Rating Aralığı |
|---|---|
| Bronz Lig (Amatör) | 0 - 119 |
| Gümüş Lig (Yarı-Profesyonel) | 120 - 149 |
| Altın Lig (Profesyonel) | 150 - 189 |
| Elit Lig (Dünya Klası) | 190 - 249 |
| Efsane Ligi | 250+ |

- Sistem **her Pazar 23:59 (sunucu saati)** ligleri yeniden hesaplar.
- Haftayı kendi liginde **1. sırada** bitiren oyuncuya otomatik **10 Gems** ödülü verilir (bkz. [Gems & Chips](/guide/systems/economy-gems-chips)).
- Sezon (haftalık ligden ayrı, aylık bir üst döngü) kavramı bu sürümde **yoktur** — yalnızca haftalık sıfırlama vardır, karışıklığı önlemek için ek bir "sezon" katmanı tasarlanmamıştır.

**Backend İhtiyaçları (uygulanacak şema ve iş):**
- `GET /api/social/leaderboard/global` zaten var ve `rating`'e göre ilk 50'yi döner (bkz. [Social & Leaderboards](/guide/systems/social-leaderboards)) — lig kümeleme bunun üzerine, sorgu anında `rating` aralığına göre **hesaplanarak** eklenebilir, ayrı bir tabloya gerek yoktur.
- Haftalık ödül dağıtımı için bir zamanlanmış görev (`backend/weekly_league_rewards.py` gibi, cron ile Pazar gecesi çalıştırılan bağımsız bir script — mevcut `daily_updater.py` scraper'ıyla karıştırılmamalı) yazılması gerekir.
