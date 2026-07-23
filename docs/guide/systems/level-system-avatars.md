# Seviye (Level) ve Avatar Sistemi

Oyuncuların profillerini geliştirdikleri, kişiselleştirdikleri ve yeteneklerini sergiledikleri gelişim mekanikleri.

## 1. XP ve Level Sistemi

::: tip Düzeltildi
Daha önce burada, `services/economy.py`'nin kullanılmayan/uyumsuz bir `add_xp()` formülü barındırdığı ve TicTacToe'nun `surrender` endpoint'inin hiç level-up tetiklemediği belirtiliyordu. İkisi de düzeltildi: kanonik per-level-bar formülü artık `services/economy.py`'deki tek bir `add_xp_and_check_level(db, user, xp_amount)` fonksiyonunda yaşıyor; hem `target_score.py`'nin `validate` endpoint'i hem `game.py`'nin `surrender` endpoint'i bu ortak fonksiyonu çağırıyor.
:::

Oyuncular, oynadıkları her (online veya offline) oyun modundan maç sonunda bir miktar XP kazanırlar ve `required_xp = 100 * level^1.5` eşiğini aşarak seviye atlarlar (`add_xp_and_check_level`, `services/economy.py` — kodda doğrulandı).

**XP Kazanım Mantığı (mod bazlı, kesin — bkz. ilgili mod sayfaları):**
- [Stats Target](/guide/game-modes/stats-target) ve [Extreme Squad](/guide/game-modes/extreme-squad): sapma yüzdesine göre 5 kademeli XP (25/25/15/10/5).
- [TicTacToe](/guide/game-modes/tictactoe-4x4): doğru hücre başına 10 XP (singleplayer `surrender` üzerinden; artık düzgün şekilde level-up tetikliyor).
- **Online Mod (genel kural):** Kazanan/kaybeden ayrımına dayalı XP miktarı şu an **kodlanmamıştır** — sadece Chip/Rating değişir (`award_winnings`, `update_rating`); online maçlardan XP kazanımı henüz backend'e eklenmemiştir. Eklenecekse en basit çözüm: kazanana sabit **50 XP**, kaybedene sabit **10 XP**, aynı `add_xp_and_check_level` fonksiyonu üzerinden `evaluate_*` fonksiyonlarının içine eklenerek.

**2x Boost:** **(Kodlanmadı)** — Gems karşılığında XP'ye süreli çarpan uygulama mekanizması yok, bkz. [Gems & Chips](/guide/systems/economy-gems-chips).

## 2. Avatar ve Özelleştirme

::: danger Kodlanmadı
`models.py`'de avatar/envanter/market ile ilgili hiçbir tablo yok (`User` tablosunda bir `avatar_id` veya benzeri alan bile yok). Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir.
:::

- **Market Alışverişi:** Oyuncular Gems veya Chips karşılığında avatarlarına özel formalar, atkılar, kramponlar, şapkalar satın alabilir.
- **Seviye Ödülleri:** Oyuncular her **10 seviyede bir** (10, 20, 30...) sistemden otomatik olarak rastgele basit bir avatar öğesi kazanır (15 değil, kesin olarak 10 — tek bir sabit aralık, karışıklığı önlemek için).

**Backend İhtiyaçları (uygulanacak şema):**
- `avatar_items` tablosu: `id`, `name`, `slot` (`forma`/`atki`/`kramponlar`/`sapka`), `price_gems`, `price_chips`, `rarity`.
- `user_inventory` tablosu: `id`, `user_id` (FK), `item_id` (FK), `acquired_at`, `source` (`'market'`/`'level_reward'`).
- `users` tablosuna `equipped_avatar_item_ids` (JSON veya ayrı `user_equipped_items` tablosu) eklenmesi, o an giyili olan öğeleri tutmak için.
- `POST /api/shop/buy` → `{"item_id": 5, "currency": "gems"|"chips"}`; bakiye kontrolü + `user_inventory`'ye ekleme.
- Level-up sırasında (yukarıdaki ortak `add_xp_and_check_level` fonksiyonu içinde) `if new_level % 10 == 0: grant_random_item(db, user)` çağrısı.
