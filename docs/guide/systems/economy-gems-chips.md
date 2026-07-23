# Gems ve Chips Ekonomisi

Sistemde iki temel para birimi bulunur: standart bakiye olan **Chips (Çip)** ve premium/nadir bakiye olan **Gems (Mücevher)**. `models.py`'deki `User.chips` (varsayılan **1000**) ve `User.gems` (varsayılan **20**) alanlarıyla birebir uygulanmıştır.

::: warning Uygulama durumu özeti
Yalnızca **Chips'in oda giriş ücreti / ödül havuzu / rake** akışı gerçekten kodlanmıştır. Gems'in kazanım yolları (IAP, haftalık lig ödülü, streak ödülü), Gems'in harcama yolları (market, 2x takviye, Chip bozdurma) ve avatar market'i **hiçbiri kodlanmamıştır** — yalnızca `User.gems` sayacı var, onu değiştiren hiçbir endpoint yok. Aşağıda her madde işaretlenmiştir.
:::

## 1. Gems (Mücevher)
Oyunun en değerli ve elde etmesi en zor para birimidir.
- **Başlangıç Bakiyesi:** Her yeni hesap **20 Gem** ile başlar (kodda doğrulandı: `models.User.gems = Column(Integer, default=20)`).

**Gems Nasıl Kazanılır?**
1. **(Kodlanmadı)** Market üzerinden gerçek para ile satın alarak (IAP - In-App Purchase) — App Store/Play Store satın alma doğrulaması backend'de yok.
2. **(Kodlanmadı)** Haftanın/sezonun sonunda, oyuncu bulunduğu ELO liginde 1. sıraya yerleşirse ödül olarak — bkz. [Rank/ELO](/guide/systems/ranking-elo), haftalık lig sistemi henüz yok.
3. **(Kodlanmadı)** 7 günlük ve katları (14, 21, 28) ardışık giriş serilerinde (streak) sadakat ödülü olarak — `User` tablosunda bir "son giriş tarihi" veya "streak sayacı" alanı yok.

**Gems Nereye Harcanır?**
1. **(Kodlanmadı)** Marketten özel avatarlar, kramponlar, atkılar satın alırken — bkz. [Level & Avatar Sistemi](/guide/systems/level-system-avatars), market/envanter şeması yok.
2. **(Kodlanmadı)** Oyun sonunda kazanılacak Çip veya XP miktarına süreli **2x Takviye (Boost)** satın alırken — `services/economy.py`'de boost/çarpan mantığı yok.
3. **(Kodlanmadı)** Çip bakiyesi tükendiğinde, Gem bozdurularak Çip satın alırken.

## 2. Chips (Çip/Para)
Oyunun günlük işleyişini sağlayan temel para birimidir; bu kısım **tamamen kodlanmış ve çalışır durumdadır**.
- **Başlangıç Bakiyesi:** Her oyuncu **1000 Chip** ile başlar (`models.User.chips = Column(Integer, default=1000)`).

**Chips Nasıl Harcanır ve Kazanılır? (kodda doğrulandı)**
- **Oda Giriş Ücretleri:** Her online oyun modunun farklı giriş ücretlerine sahip odaları vardır — kesin tier listesi: `100, 250, 400, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000, 10000000` Chip (`ROOM_TIERS`, `backend/socket_manager.py`). Oyuncu odaya girerken bu ücreti öder (`deduct_entry_fee`, `services/economy.py`); yetersiz bakiyede giriş reddedilir.
- **Ödül Havuzu:** Masadaki toplam giriş ücreti (2 kişi × giriş ücreti) ödül havuzunu oluşturur. Kazanan bu havuzun **%90'ını** alır; **%10 sistem kesintisidir (rake)** — `award_winnings`, `RAKE_PERCENTAGE = 0.10` sabiti.
- **Beraberlik:** Kazanan yoksa (her modun kendi sayfasındaki "Beraberlik" kuralına bkz.) oda ücreti **aynen iade edilir**, rake kesilmez.
- **Diğer kazanım yolları (Gem karşılığı market, 2x takviye):** **(Kodlanmadı)** — yukarıdaki Gems bölümündeki nedenlerle henüz yok.
