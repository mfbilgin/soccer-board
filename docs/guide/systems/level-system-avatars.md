# Seviye (Level) ve Avatar Sistemi

Oyuncuların profillerini geliştirdikleri, kişiselleştirdikleri ve yeteneklerini sergiledikleri gelişim mekanikleri.

## 1. XP ve Level Sistemi
Oyuncular, oynadıkları her (online veya offline) oyun modundan maç sonunda bir miktar XP kazanırlar ve `required_xp = 100 * level^1.5` eşiğini aşarak seviye atlarlar. XP bir "seviye barı" gibi davranır: eşik dolduğunda XP'den düşülür ve level artar (tek istekte birden fazla seviye atlanabilir). Bu hesaplama tüm modlarda **tek, ortak bir fonksiyon** üzerinden yapılır, her modun kendi XP mantığını tekrar yazmasına gerek yoktur.

**XP Kazanım Mantığı (mod bazlı — bkz. ilgili mod sayfaları):**
- [Stats Target](/guide/game-modes/stats-target) ve [Extreme Squad](/guide/game-modes/extreme-squad): sapma yüzdesine göre 5 kademeli XP (25/25/15/10/5).
- [TicTacToe](/guide/game-modes/tictactoe-4x4): doğru hücre başına 10 XP (singleplayer, pes etme akışı üzerinden).
- **Online Mod (genel kural):** Kazanan/kaybeden ayrımına dayalı XP miktarı henüz tanımlı değildir — online maçlarda yalnızca Chip (ödül havuzu) ve Rating (ELO) değişir. Eklenecekse en basit çözüm: kazanana sabit **50 XP**, kaybedene sabit **10 XP**.

**2x Boost:** Gems karşılığında XP'ye süreli çarpan uygulama. *Durum: kodlanmadı* (bkz. [Gems & Chips](/guide/systems/economy-gems-chips)).

## 2. Avatar ve Özelleştirme

*Durum: kodlanmadı. Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir.*

- **Market Alışverişi:** Oyuncular Gems veya Chips karşılığında avatarlarına özel formalar, atkılar, kramponlar, şapkalar satın alabilir.
- **Seviye Ödülleri:** Oyuncular her **10 seviyede bir** (10, 20, 30...) sistemden otomatik olarak rastgele basit bir avatar öğesi kazanır.

**Backend Sözleşmesi:**
- `avatar_items` tablosu: `id`, `name`, `slot` (`forma`/`atki`/`kramponlar`/`sapka`), `price_gems`, `price_chips`, `rarity`.
- `user_inventory` tablosu: `id`, `user_id` (FK), `item_id` (FK), `acquired_at`, `source` (`'market'`/`'level_reward'`).
- `users` tablosuna, o an giyili olan öğeleri tutmak için `equipped_avatar_item_ids` (JSON veya ayrı bir `user_equipped_items` tablosu) eklenmesi gerekir.
- `POST /api/shop/buy` → `{"item_id": 5, "currency": "gems"|"chips"}`; bakiye kontrolü + `user_inventory`'ye ekleme.
- Level-up sırasında, ortak XP/level fonksiyonu içinde `if new_level % 10 == 0: grant_random_item(db, user)` çağrısı yapılır.
