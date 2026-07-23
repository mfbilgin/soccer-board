# Gems ve Chips Ekonomisi

Sistemde iki temel para birimi bulunur: standart bakiye olan **Chips (Çip)** ve premium/nadir bakiye olan **Gems (Mücevher)**.

## 1. Gems (Mücevher)
Oyunun en değerli ve elde etmesi en zor para birimidir.
- **Başlangıç Bakiyesi:** Her yeni hesap **20 Gem** ile başlar.

**Gems Nasıl Kazanılır?**
1. Market üzerinden gerçek para ile satın alarak (IAP - In-App Purchase). *Durum: kodlanmadı — App Store/Play Store satın alma doğrulama akışı gerekir.*
2. Haftanın/sezonun sonunda, oyuncu bulunduğu ELO liginde 1. sıraya yerleşirse ödül olarak (bkz. [Rank/ELO](/guide/systems/ranking-elo)). *Durum: kodlanmadı.*
3. 7 günlük ve katları (14, 21, 28) ardışık giriş serilerinde (streak) sadakat ödülü olarak. *Durum: kodlanmadı — kullanıcı kaydında bir "son giriş tarihi" ve "streak sayacı" alanı gerekir.*

**Gems Nereye Harcanır?**
1. Marketten özel avatarlar, kramponlar, atkılar satın alırken (bkz. [Level & Avatar Sistemi](/guide/systems/level-system-avatars)). *Durum: kodlanmadı.*
2. Oyun sonunda kazanılacak Çip veya XP miktarına süreli **2x Takviye (Boost)** satın alırken. *Durum: kodlanmadı.*
3. Çip bakiyesi tükendiğinde, Gem bozdurularak Çip satın alırken. *Durum: kodlanmadı.*

## 2. Chips (Çip/Para)
Oyunun günlük işleyişini sağlayan temel para birimidir.
- **Başlangıç Bakiyesi:** Her oyuncu **1000 Chip** ile başlar.

**Chips Nasıl Harcanır ve Kazanılır?**
- **Oda Giriş Ücretleri:** Her online oyun modunun farklı giriş ücretlerine sahip odaları vardır. Kesin tier listesi: `100, 250, 400, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000, 2500000, 5000000, 10000000` Chip. Oyuncu odaya girerken bu ücreti öder; yetersiz bakiyede giriş reddedilir.
- **Ödül Havuzu:** Masadaki toplam giriş ücreti (2 kişi × giriş ücreti) ödül havuzunu oluşturur. Kazanan bu havuzun **%90'ını** alır; **%10 sistem kesintisidir (rake)**.
- **Beraberlik:** Kazanan yoksa (her modun kendi sayfasındaki "Beraberlik" kuralına bkz.) oda ücreti aynen iade edilir, rake kesilmez.
- **Diğer kazanım yolları (Gem karşılığı market, 2x takviye):** *Durum: kodlanmadı — yukarıdaki Gems bölümüne bağlıdır.*
