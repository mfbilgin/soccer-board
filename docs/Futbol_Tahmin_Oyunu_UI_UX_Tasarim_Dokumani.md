# Futbol Tahmin Oyunu — UI/UX Tasarım Dokümanı & Ekran Spesifikasyonları

| Alan | Bilgi |
|------|-------|
| Doküman Türü | UI/UX Tasarım Brief'i + Ekran Spesifikasyonları |
| Versiyon | 1.0 |
| Kaynak | Futbol Tahmin Oyunu GDD v1.1 |
| Hedef Okuyucu | UI/UX Tasarımcısı |
| Platform | iOS + Android (mobil öncelikli), Faz 4: Web |
| Tarih | 28 Haziran 2026 |

> **Bu dokümanın amacı:** Bir UI/UX tasarımcısının, başka hiçbir belgeye ihtiyaç duymadan uygulamanın tüm ekranlarını, akışlarını, durumlarını ve bileşenlerini tasarlayabilmesi. Her ekran için **amaç, içerik, yerleşim mantığı, etkileşimler, durumlar ve kenar durumları** verilmiştir. Görsel stil kararları (renk, tipografi, marka) bilinçli olarak tasarımcıya bırakılmıştır; bu doküman *ne* gerektiğini ve *nasıl davranması* gerektiğini tanımlar, *nasıl görüneceğini* değil.

---

## İçindekiler

1. Tasarımcıya Brief
2. Tasarım Sistemi Gereksinimleri
3. Bilgi Mimarisi (IA) ve Navigasyon
4. Global / Ortak Bileşenler
5. Onboarding ve Giriş Akışı
6. Ana Ekranlar (Meta)
7. Oyun Akışı (Mod Seçim → Oda → Eşleştirme → Sonuç)
8. Oyun Ekranları (11 Mod — Detaylı)
9. Rekabet Ekranları (Lig, Lider Tabloları)
10. Ekonomi ve Market Ekranları
11. Profil, Avatar, Başarımlar
12. Sosyal Ekranlar
13. Ayarlar ve Sistem Ekranları
14. Ekran Durumları (States) — Genel Kurallar
15. Mikro-etkileşimler ve Animasyon
16. Erişilebilirlik Kontrol Listesi
17. Metin / Mikrocopy İhtiyaçları
18. Responsive ve Cihaz Notları
19. Tasarımcıdan Beklenen Teslimatlar
20. Tasarım Önceliği (MVP → Sonra)
21. Tasarımcının Karar Vermesi Gerekenler

---

## 1. Tasarımcıya Brief

### 1.1. Ürün Tek Cümlede
Futbol meraklılarının bilgisini hızlı, rekabetçi mini oyunlarla test eden; çevrimiçi (çok oyunculu) ve tek oyunculu oynanabilen, ekonomi + lig + level sistemi olan bir mobil futbol tahmin oyunu.

### 1.2. Tasarımın Çözmesi Gereken Temel Gerilim
Bu üründe **11 farklı oyun modu** var ama hepsi **tek bir tutarlı uygulama** gibi hissettirmeli. Tasarımcının en büyük görevi:
- Her modun **kendine özgü** ve net bir oyun ekranı olması,
- Ama tüm modların **ortak bir tasarım dili, navigasyon ve meta katman** (para, level, süre, sonuç) paylaşması.

### 1.3. Tasarım İlkeleri (Pusula)
Her tasarım kararı bu ilkelere göre değerlendirilmeli:
1. **Hız.** Oyuncu en fazla 2 dokunuşta oyuna girebilmeli. Her tek el 30–180 sn. Sürtünme düşmanımız.
2. **Anında anlaşılırlık.** Oyuncu bir oyun ekranını ilk gördüğünde "ne yapmam gerektiğini" saniyeler içinde anlamalı.
3. **Tatmin edici geri bildirim.** Doğru/yanlış, kazanç, level atlama gibi anlar görsel + (opsiyonel) haptik olarak ödüllendirici olmalı.
4. **Adil ve şeffaf.** Süre, hak, ödül, rakip durumu her zaman net görünmeli.
5. **Erişilebilir.** Renk körlüğü ve düşük görüş dahil herkes oynayabilmeli (bkz. §16).

### 1.4. Hedef Kitle
- **Birincil:** 16–35 yaş, futbolu yakından takip eden, "hardcore" taraftarlar.
- **İkincil:** Casual futbol izleyicileri (görsel/kolay modlarla giriş yapar).
- Mobil-yerli kullanıcılar; çoğu tek elle, hareket halinde oynar → **tek el kullanımı (one-handed)** önemli.

### 1.5. Tonal Yön
Rekabetçi ama eğlenceli, enerjik, modern. Saha/stadyum çağrışımları olabilir ama arayüz temiz ve okunaklı kalmalı. Belirli bir kulübe/taraftarlığa yaslanmayan, evrensel bir kimlik.

---

## 2. Tasarım Sistemi Gereksinimleri

> Görsel kimlik henüz belirlenmedi. Tasarımcının **bir tasarım sistemi (design system) kurması beklenir.** Aşağıda bu sistemin içermesi gerekenler ve uyması gereken kısıtlar var.

### 2.1. Renk
Tasarımcı şunları tanımlamalı:
- **Marka renkleri:** Birincil + ikincil/vurgu (CTA).
- **Nötr skala:** Arka plan, yüzey, kenarlık, metin için kademeli griler (açık/koyu).
- **Anlamsal renkler:** Başarı, hata, uyarı, bilgi.
- **Para birimi renkleri:** Gems ve Chip için ayırt edici, tutarlı renk/ikon.
- **Lig tier renkleri:** Bronz, Gümüş, Altın, Platin, Elmas, Efsane.

**Kısıt (zorunlu):**
- **Renk asla tek başına anlam taşımaz** (renk körlüğü). Doğru/yanlış, yeşil/kırmızı durumlar her zaman ikon/şekil/etiketle desteklenir (bkz. §16).
- Kontrast oranları en az WCAG AA (normal metin 4.5:1, büyük metin 3:1).
- **Karanlık mod (dark mode):** Tasarlanması beklenir (oyun gece/kapalı ortamda çok oynanır). En azından MVP sonrası; sistem baştan iki temaya uygun token'larla kurulmalı.

### 2.2. Tipografi
- En fazla 2 yazı ailesi (başlık + gövde).
- Net bir **rakam/sayı stili** (skor, süre, para çok kullanılır — okunaklı, hızlı taranabilir tabular rakamlar).
- Tip ölçeği (type scale): başlık, alt başlık, gövde, etiket, mikro.
- Dinamik yazı boyutu desteği (erişilebilirlik).

### 2.3. Boşluk, Izgara, Köşe
- Tutarlı spacing skalası (örn. 4/8 tabanlı).
- Mobil için kenar boşlukları (safe area / notch / home indicator dikkate alınmalı).
- Köşe yuvarlama, gölge/elevation token'ları.

### 2.4. İkonografi
Tasarımcı tutarlı bir ikon seti üretmeli. Gerekli ikonlar (en az):
- Para: Gems, Chip
- Mevkiler: Kaleci, Defans, Ortasaha, Forvet
- Modlar: 11 modun her biri için ayırt edici simge
- Durum: doğru (✓), yanlış (✗), süre/saat, can/hak, kilit, bilgi (?), uyarı
- Navigasyon: ana sekmeler, geri, kapat, ayarlar, paylaş, arkadaş ekle
- Ödül: hediye, sandık, level rozeti, başarım rozeti

### 2.5. Bileşen Kütüphanesi (Component Library)
Yeniden kullanılabilir bileşenler tasarlanmalı (her biri tüm durumlarıyla — bkz. §4 ve §14):
- Butonlar (birincil, ikincil, üçüncül, ikon buton, tehlike), durumlar: normal/basılı/devre dışı/yükleniyor
- Metin giriş alanı + **autocomplete açılır listesi** (oyunun kalbi — bkz. §4.4)
- Kartlar (mod kartı, oda kartı, oyuncu/takım kartı, ödül kartı)
- Modal / dialog / alt sayfa (bottom sheet)
- Toast / snackbar / inline uyarı
- Sayaç (timer) — dairesel ve/veya çubuk
- İlerleme çubuğu (level XP, hedefe uzaklık)
- Avatar bileşeni (katmanlı)
- Para göstergesi (üst bar)
- Lider tablosu satırı
- Rozet/etiket (lig, başarım, "Yeni")
- Boş durum (empty state) şablonu
- Yükleniyor (skeleton/spinner) şablonu

### 2.6. Avatar Sistemi
Katmanlı ve genişletilebilir: forma, atkı, krampon, şapka, arka plan, çerçeve (+ ileride saç, yüz vb.). Tasarımcı, parçaların üst üste tutarlı bindiği bir **katman sistemi** kurmalı.

---

## 3. Bilgi Mimarisi (IA) ve Navigasyon

### 3.1. Ana Navigasyon — Alt Sekme Çubuğu (Bottom Tab Bar)
Mobil standart, tek el erişimi için alt navigasyon önerilir. **5 ana sekme:**

```
[ Oyna ]   [ Sıralama ]   [ Market ]   [ Sosyal ]   [ Profil ]
   🎮           🏆            🛒           👥           👤
```

| Sekme | İçerik |
|-------|--------|
| **Oyna (Home)** | Ana ekran: mod seçimi, günlük ödül, hızlı oyna, streak |
| **Sıralama** | Lig durumu + lider tabloları (global / ülke / arkadaş / mod) |
| **Market** | Gems/Chip paketleri, avatar parçaları, takviyeler, battle pass |
| **Sosyal** | Arkadaşlar, davet, özel oda, piramit akışı |
| **Profil** | Avatar, istatistikler, başarımlar, ayarlar girişi |

> **Not:** "Oyna" varsayılan açılış sekmesidir. Oyun oturumu sırasında (oyun ekranı, eşleştirme) sekme çubuğu **gizlenir** — tam ekran odak.

### 3.2. Ekran Haritası (Screen Map)
```
Açılış
 ├─ Splash
 ├─ Giriş / Kayıt (Google / Apple / E-posta)
 └─ Onboarding (hoşgeldin + bonus + ilk tutorial)

Oyna (Tab)
 ├─ Ana Menü
 ├─ Mod Seçim ─ (online/tek oyunculu)
 │   ├─ Oda Seçim (online) ─ Eşleştirme ─ [OYUN EKRANI] ─ Sonuç
 │   └─ [OYUN EKRANI] (tek oyunculu) ─ Sonuç
 ├─ Mod Tutorial (ilk girişte)
 └─ Günlük Görevler / Ödül

Sıralama (Tab)
 ├─ Lig (mevcut hafta, terfi/düşme barajı)
 ├─ Global Lider Tablosu
 ├─ Ülke Lider Tablosu
 ├─ Arkadaş Sıralaması
 └─ Mod Bazlı Sıralama

Market (Tab)
 ├─ Gems paketleri (IAP)
 ├─ Chip paketleri
 ├─ Avatar mağazası
 ├─ Takviyeler (2x XP / 2x Chip)
 └─ Battle Pass / Sezon Geçişi

Sosyal (Tab)
 ├─ Arkadaş listesi
 ├─ Arkadaş ekle / davet
 ├─ Özel oda kur / katıl
 └─ Piramit akışı (keşfet)

Profil (Tab)
 ├─ Profil özeti (avatar, level, rating, lig)
 ├─ Avatar özelleştirme
 ├─ İstatistikler
 ├─ Başarımlar
 └─ Ayarlar
     ├─ Hesap (giriş yöntemleri, çıkış)
     ├─ Ses / Müzik / Haptik
     ├─ Erişilebilirlik (renk körü modu, yazı boyutu)
     ├─ Bildirimler
     ├─ Dil
     └─ Gizlilik / Yasal / Destek
```

### 3.3. Navigasyon İlkeleri
- Oyun ekranından çıkış her zaman **onay** ister (devam eden online maçta hükmen yenilgi uyarısı — bkz. §8 ortak kurallar).
- Geri/kapat davranışı tutarlı (üst sol geri, üst sağ kapat).
- Derin linkler: bildirimden doğrudan ilgili ekrana (örn. "arkadaşın seni davet etti" → özel oda).

---

## 4. Global / Ortak Bileşenler

Bu bileşenler birçok ekranda tekrarlanır; bir kez tutarlı tasarlanıp her yerde kullanılır.

### 4.1. Üst Bar (Top Bar) — Kaynak Göstergesi
Meta ekranların üstünde sürekli görünür:
- Sol: kullanıcı avatarı (mini) + level rozeti → dokununca Profil.
- Orta/Sağ: **Gems** ve **Chip** bakiyesi (ikon + sayı) → yanındaki "+" ile Market'e kısa yol.
- Bakiye değişiminde küçük animasyon (artış/azalış).

### 4.2. Sayaç (Timer)
- Online tüm tur bazlı modlarda görünür.
- Görsel: dairesel halka veya üst çubuk; son ~5 sn'de renk + (opsiyonel) titreşim/ses ile aciliyet.
- Renk körlüğü: aciliyet sadece renkle değil, **dolum oranı + sayı + animasyon** ile de gösterilir.

### 4.3. Hak / Can Göstergesi
- 3 hak gibi durumlarda 3 ikon (örn. dolu/boş); yanlışta bir tanesi "tükenir" animasyonu.

### 4.4. Futbolcu/Takım Giriş Alanı + Autocomplete (KRİTİK BİLEŞEN)
Bu, oyunun en çok kullanılan etkileşimi. Çok modda tekrarlanır; mükemmel olmalı.
- Kullanıcı yazmaya başlar → anlık öneri listesi açılır.
- Her öneri satırı: **isim + ayırt edici bilgi** (örn. uyruk bayrağı, doğum yılı, son kulüp) — eşadlıları ayırmak için.
- Türkçe/uluslararası karakter ve aksan toleransı (kullanıcı "ozil" yazınca "Özil" çıkmalı).
- Lakap desteği (örn. "Pele" → Pelé).
- Seçim dokunmayla yapılır (serbest metin kabul edilmez → yazım hatası/bilinmeyen oyuncu sorununu önler).
- Durumlar: yazılıyor, öneri var, öneri yok ("bulunamadı"), geçersiz (kapsam dışı oyuncu → açıklayıcı uyarı, hak yanmaz).
- Performans hissi: öneriler gecikmesiz gelmeli (algı olarak anlık).

### 4.5. Oyuncu / Takım Kartı (Chip/Token)
Seçilen oyuncu veya takımı temsil eden küçük kart: görsel/silüet/baş harf + isim + (bağlama göre) istatistik. Kaldırılabilir (x).

### 4.6. Sonuç Bildirimi (Doğru/Yanlış)
- Doğru: yeşil + ✓ ikonu + olumlu animasyon/ses.
- Yanlış: kırmızı + ✗ ikonu + nazik geri bildirim (oyuncuyu cezalandırıcı/utandırıcı değil).
- **Renk körlüğü:** ikon her zaman renge eşlik eder.

### 4.7. Modal / Alt Sayfa (Bottom Sheet)
- Onay diyalogları (çıkış, satın alma, teslim).
- Bilgi/eğitim kartları.
- "Nasıl oynanır" (mod tutorial tekrarı).

### 4.8. Boş Durum (Empty State) ve Hata Şablonları
Bkz. §14 — her liste/ekran için tutarlı boş ve hata şablonu.

---

## 5. Onboarding ve Giriş Akışı

### 5.1. Splash
- Marka logosu; arka planda yükleme. Minimum süre, hızlı geçiş.

### 5.2. Giriş / Kayıt
- **Kayıt zorunludur** (misafir oyun yok).
- Seçenekler: **Google ile devam et**, **Apple ile devam et**, **E-posta ile devam et**.
- E-posta akışı: e-posta + şifre, doğrulama, şifre sıfırlama linki.
- iOS'ta Google sunuluyorsa Apple ile Giriş de görünür olmalı (politika).
- Cihazlar arası senkron mesajı: "İlerlemen tüm cihazlarında seninle."
- Hata durumları: bağlantı yok, geçersiz bilgi, e-posta zaten kayıtlı, doğrulama bekleniyor.

### 5.3. Hoşgeldin & Başlangıç Bonusu
- "Hoş geldin!" + **20 Gems ve 1000 Chip** hediyesi animasyonlu verilir.
- Çok kısa, atlanamaz olmayan (skip mümkün) bir karşılama.

### 5.4. İlk Tutorial
- Kolay bir tek oyunculu mod (örn. Bayrak XI veya İlk 10) ile **yaparak öğrenme**.
- Risksiz (Chip harcamaz). Adım adım ipucu balonları.
- Bitince Ana Menü'ye düşer.

### 5.5. İzinler
- Bildirim izni (streak/davet hatırlatmaları için) — değer önerisiyle, doğru anda istenmeli (hemen değil, ilk değerli andan sonra).

---

## 6. Ana Ekranlar (Meta)

### 6.1. Ana Menü (Home / "Oyna" sekmesi)
**Amaç:** Oyuncuyu en hızlı şekilde oyuna sokmak + günlük geri dönüş kancalarını göstermek.

**İçerik (öncelik sırasıyla):**
- Üst bar (avatar+level, Gems, Chip — §4.1).
- **Birincil CTA: "Hızlı Oyna"** (son/önerilen modu tek dokunuşla başlatır) — en belirgin eleman.
- **Mod galerisi:** 11 modun kartları (kaydırılabilir grid/liste). Her kart: mod ikonu, adı, kısa açıklama, "Yeni" rozeti (oynanmamışsa).
- **Günlük ödül / streak:** mevcut streak günü, sıradaki ödül, "topla" aksiyonu.
- **Günlük görevler:** kısa özet + ilerleme.
- **Lig durumu kısayolu:** mevcut lig + haftalık sıra (mini), Sıralama sekmesine link.
- (Opsiyonel) Aktif etkinlik/sezon banner'ı.

**Durumlar:** ödül alınabilir (vurgulu) vs alınmış; yeni mod var; etkinlik aktif.

### 6.2. Günlük Ödül / Streak Ekranı
- Gün gün ilerleyen ödül takvimi (7 ve katlarında Gems vurgulu).
- Bugünün ödülü "topla" animasyonu.
- Streak bozulma uyarısı (geri kazanım kancası).

### 6.3. Günlük Görevler
- Liste: görev + ilerleme (örn. "2/3 maç kazan") + ödül.
- Tamamlanan görevde "topla".

---

## 7. Oyun Akışı (Mod Seçim → Oda → Eşleştirme → Sonuç)

### 7.1. Mod Seçim Ekranı
**Amaç:** Modu ve oynanış türünü (online / tek oyunculu) seçtirmek.
- Seçilen modun açıklaması + "Nasıl oynanır" (?) butonu (tutorial'ı tekrar açar).
- **Online / Tek Oyunculu anahtarı** (segmented control veya toggle).
- Bazı modlar yalnızca online'dır (Kesişim Düellosu, Zincir) → tek oyunculu seçeneği pasif/gizli olmalı, nedeni belirtilmeli.
- Online seçilirse → Oda Seçim'e; tek oyunculu seçilirse → doğrudan oyuna.

### 7.2. Oda Seçim Ekranı (yalnızca online)
**Amaç:** Bahis seviyesini seçtirmek.
- Oda kartları: **Acemi / Standart / Yüksek / VIP** — her birinde giriş ücreti (Chip), tahmini ödül havuzu, oyuncu kapasitesi.
- Kullanıcının Chip bakiyesi görünür; yetersizse oda pasif + "Chip al" kısayolu.
- "Kazanan havuzun %90'ını alır" gibi şeffaf bilgi.
- Seçince → onay (ücret kesilecek) → Eşleştirme.

### 7.3. Eşleştirme (Matchmaking) Ekranı
**Amaç:** Rakip ararken oyuncuyu bilgilendirmek ve oyalamak.
- "Rakip aranıyor…" animasyonu + süre/dönen gösterge.
- Bulununca: rakibin avatarı, adı, level/rating "VS" düzeniyle gösterilir → kısa geri sayım → oyun başlar.
- **Bot yok** → uzun sürebilir: iptal butonu her zaman erişilebilir; uzarsa "Tek oyunculu dene" önerisi.
- Durumlar: aranıyor, rakip bulundu, iptal, bağlantı hatası.
- Çok oyunculu (Zincir) için: katılımcılar dolarken liste gösterimi.

### 7.4. Oyun Ekranı (Genel İskelet)
Tüm 11 modun paylaştığı ortak çerçeve (mod içeriği ortada değişir):
```
┌─────────────────────────────────────┐
│  [çıkış]   MOD ADI / TUR   [sayaç]   │  ← üst bilgi
│  Rakip(ler) durumu / skor            │  ← online'da
├─────────────────────────────────────┤
│                                       │
│        MODA ÖZEL OYUN ALANI           │  ← §8'de her mod
│                                       │
├─────────────────────────────────────┤
│   Giriş alanı / aksiyon / hak         │  ← alt etkileşim
└─────────────────────────────────────┘
```
- **Çıkış:** her zaman onay ister; online'da "çıkarsan yenilirsin" uyarısı.
- Süre, skor, hak her an görünür.

### 7.5. Sonuç Ekranı
**Amaç:** Sonucu net göstermek + ödülü tatmin edici sunmak + tekrar oynamaya yönlendirmek.
- **Sonuç başlığı:** Kazandın / Kaybettin / Berabere (renk + ikon + metin — renk körü uyumlu).
- **Ödül akışı (animasyonlu):** kazanılan Chip, XP (bar dolumu), Rating değişimi (+/−).
- **Level atladıysa:** özel kutlama + ödül.
- **Lig etkisi:** terfi/düşme barajına etki (varsa mini gösterim).
- Online: rakiple karşılaştırma (skor/süre).
- **Aksiyonlar:** "Tekrar Oyna" (birincil), "Mod Değiştir", "Ana Menü", "Paylaş" (özellikle iyi sonuçlarda).
- Başarım açıldıysa: rozet bildirimi.
- Durumlar: zafer / yenilgi / beraberlik / bağlantı kopması nedeniyle bitiş.

---

## 8. Oyun Ekranları (11 Mod — Detaylı)

> Her mod için: **Amaç · Ekrandaki ana öğeler · Etkileşim akışı · Online vs Tek oyunculu farkı · Özel durumlar · Tasarım notları.** Kurallar GDD'den gelir; burada odak **arayüz ve etkileşim**.

### 8.1. Kariyer İstatistiği Avı (Hedef Tutturma)
**Amaç:** Sabit sayıda futbolcuyla bir istatistik hedefine **en yakın** toplamı yakalamak.

**Ana öğeler:**
- **Hedef başlığı:** Net ve büyük → "La Liga · Toplam Gol · Hedef: 500 · 3 futbolcu".
- **Futbolcu slotları:** Sabit sayı kadar boş slot (örn. 3). Her slot doldukça futbolcu kartı + katkısı.
- **Toplam & uzaklık göstergesi:** Anlık toplam ve **hedefe uzaklık** (örn. "+12" / "−40") — renk + işaret + sayı ile.
- **Giriş alanı:** Autocomplete (§4.4).

**Akış:** Slot seç/yaz → futbolcu ekle → toplam ve uzaklık güncellenir → tüm slotlar dolunca "Onayla/Bitir".

**Online vs Tek oyunculu:** Online'da rakibin slot ilerlemesi (kaç slot doldu) görünür; isimler gizli. Sonuçta toplamlar karşılaştırılır. Tek oyunculuda yalnızca kişisel sonuç + rekor.

**Özel durumlar:** Kapsam dışı/aynı oyuncu → uyarı, hak yanmaz. Eşit uzaklık → beraberlik (Sonuç ekranında belirtilir).

**Tasarım notu:** Uzaklık göstergesi oyunun kalbi — alt mı üst mü olduğu (hedefi aştın/altında kaldın) anında okunmalı.

---

### 8.2. Sınırlı XI Kadro Kurma
**Amaç:** Bir kritere göre (en genç/en uzun) 1-4-3-3 dizilimde, her biri **farklı takımda aktif** 11 futbolcuyla en uç kadroyu kurmak.

**Ana öğeler:**
- **Kriter başlığı:** "En Genç XI" / "En Uzun XI".
- **Saha görünümü:** 1-4-3-3 dizilimde 11 mevki slotu (Kaleci 1 / Defans 4 / Ortasaha 3 / Forvet 3). Boş slotlar mevki etiketli.
- **Toplam skor göstergesi:** Anlık toplam yaş/boy (örn. "Toplam yaş: 211").
- **Kullanılan takımlar:** Benzersizlik kuralı için, seçilmiş takımları gösteren/uyaran bir gösterge.
- **Giriş alanı:** Slota dokun → o role uygun futbolcu ara (autocomplete) → yerleştir.

**Akış:** Boş mevkiye dokun → arama → seç → saha güncellenir → tüm slotlar dolunca "Onayla".

**Online vs Tek oyunculu:** Online'da süre + sonra skor karşılaştırması. Tek oyunculuda kişisel rekor.

**Özel durumlar:** Aynı takımdan ikinci oyuncu → engellenir + açıklama ("Milan zaten kullanıldı"). Role uygun olmayan oyuncu → uyarı.

**Tasarım notu:** Saha metaforu görseli güçlendirir; ama küçük ekranda 11 slot + skor + arama sığmalı. Belki saha + altta kayan arama paneli.

---

### 8.3. Futbol Tic-Tac-Toe (4×4)
**Amaç:** Izgara hücrelerini doğru cevaplarla doldurup 3'lü dizi yapmak.

**Ana öğeler:**
- **4×4 ızgara:** İlk satır + ilk sütun **başlık** (Tür A: takımlar/logolar; Tür B: oyuncu isimleri). Kalan 3×3 = 9 doldurulabilir hücre.
- **Sıra göstergesi:** Kimin sırası (oyuncu renk + sembol).
- **Oyuncu sembolleri:** Her oyuncu renk **ve** sembolle ayrılır (X/O veya ●/▲ — renk körlüğü).
- **Giriş:** Boş hücreye dokun → kesişim koşulu hatırlatması (örn. "Barcelona ∩ Brezilya") → autocomplete ile cevap.

**Akış:** Sıra sende → hücre seç → cevap yaz → doğruysa hücre senin sembolün/rengin; yanlışsa sıra rakibe → 3'lü dizi olunca kazanırsın → dizi olmadan dolar/kilitlenirse **yeni matris** gelir, oyun sürer.

**Online vs Tek oyunculu:** Tek oyunculuda tek kişi 9 hücreyi doldurmaya çalışır (süre/hata limiti).

**Özel durumlar:** Yeni matris geçişi net animasyonla ("Yeni tahta!"). Başlık logoları yoksa baş harf/jenerik temsil.

**Tasarım notu:** 4×4 + başlıklar küçük ekranda sıkışık olabilir → hücre boyutu, başlık okunaklılığı kritik. Seçili hücre belirgin vurgulanmalı.

---

### 8.4. İlk 10 Listesi
**Amaç:** Bir metrikte ilk 10 futbolcuyu (ilk 3 açık) doğru tahmin etmek.

**Ana öğeler:**
- **Başlık:** "Süper Lig · Tüm Zamanlar · En Çok Gol · İlk 10".
- **10 dikey kutu:** Sıra numarası + isim. İlk 3 dolu gelir; kalan 7 boş/gizli.
- **Hak göstergesi:** 3 yanlış hakkı (3 can).
- **Giriş alanı:** Autocomplete; doğru isim otomatik doğru sırasına yerleşir (oyuncu sıra tahmin etmez).
- **Puan göstergesi (online):** Doğru tahminde sıra no kadar puan; toplanan puan görünür.

**Akış:** İsim yaz → listede varsa kendi sırasına yerleşir (animasyon) → yoksa hak eksilir → liste dolunca veya haklar bitince biter.

**Online vs Tek oyunculu:** Online'da sırayla tahmin + puan yarışı + rakip puanı görünür. Tek oyunculuda yarışma yok, sadece listeyi açma.

**Özel durumlar:** Zaten açık olan ismi tekrar yazma (nazik uyarı, hak yanmamalı). Hak bitince kalan gizli isimler açıklanır mı? (Tasarımcı: öğretici olması için açmak iyi olur.)

**Tasarım notu:** Bir ismin doğru sırasına "uçup oturması" tatmin edici bir mikro-animasyon olmalı.

---

### 8.5. Kesişim Düellosu (yalnızca online)
**Amaç:** İki kriterin (takım+ülke veya takım+takım) kesişimindeki bir futbolcuyu rakipten önce bulmak.

**Ana öğeler:**
- **İki kriter büyük gösterim:** örn. [AC Milan] ∩ [Brezilya] — logolar/bayrak ile.
- **Hızlı giriş alanı:** Autocomplete, hız esas.
- **Süre + rakip durumu:** Sayaç; "rakip yazıyor…" benzeri canlı sinyal (opsiyonel).

**Akış:** Kriterler belirir → ilk geçerli cevabı giren kazanır → kimse bulamazsa süre dolar → beraberlik.

**Tasarım notu:** Saf hız oyunu → giriş alanı ekranı açılır açılmaz odakta (klavye hazır) olmalı. Gereksiz hiçbir şey dikkat dağıtmamalı.

---

### 8.6. Kariyer İzi (Transfer Tahmini)
**Amaç:** Verilen kariyer zincirinden futbolcuyu tahmin etmek.

**Ana öğeler:**
- **Kariyer zinciri görseli:** Kulüpler ok/akış ile dizili (logolar/isim), opsiyonel yıllar. Gizli kulüpler "???" (zorluğa göre).
- **Tahmin giriş alanı:** Autocomplete.
- **Hak göstergesi:** Tek oyunculuda 5 hak; her yanlışta bir "???" kulüp açılabilir (ipucu).

**Akış:** Zinciri incele → tahmin et → doğruysa zafer; yanlışsa (tek oyunculu) hak eksilir + ipucu açılır.

**Online vs Tek oyunculu:** Online'da ilk bilen kazanır (hız + süre); tek oyunculuda 5 hak + kademeli ipucu.

**Tasarım notu:** Zincir yatay kaydırılabilir olmalı (uzun kariyerler). Loan dönemleri "(kiralık)" etiketiyle ayırt edilir.

---

### 8.7. Sıralama Piramidi (sosyal, yarışma değil)
**Amaç:** Bir oyuncu/takımın "en iyiler" sıralamasındaki yerini piramide işlemek ve yayınlamak.

**Ana öğeler:**
- **Özne seçimi:** Oyuncu veya takım ara (autocomplete) → piramidin tepesinde gösterilir.
- **Piramit:** 6 katman, aşağıdan yukarı **50 → 25 → 10 → 5 → 3 → 1**.
- **Karar etkileşimi:** Her katman için Evet/Hayır. İlk "evet"ler **yeşil + ✓ + dolu desen**; ilk "hayır"dan sonrası **kırmızı + ✗ + farklı desen**.
- **Yayınla butonu:** Tamamlanınca, kullanıcı onayıyla akışa yayınlama.

**Akış:** Özne seç → alttan başlayarak katman katman evet/hayır → piramit renklenir → "Yayınla".

**Sosyal görünüm:** Yayınlanan piramitler akışta (Sosyal sekmesi); diğer kullanıcılar **katılıyorum/katılmıyorum** + beğeni; "topluluk %72 katılıyor" gibi toplu görünüm.

**Tasarım notu:** Bu mod paylaşıma çok uygun → **paylaşılabilir görsel kart** (sosyal medya için) tasarlanmalı. Renk körlüğü için katman durumu mutlaka ikon/desenle.

---

### 8.8. Harf Düellosu (Baş/Son Harf)
**Amaç:** Soyadı belirli harfle başlayıp belirli harfle biten futbolcuyu bulmak.

**Ana öğeler:**
- **İki harf büyük gösterim:** [Başlangıç: B] … [Bitiş: O] → "B___O".
- **Giriş alanı:** Autocomplete.
- **Sayaç:** 30 sn belirgin.
- **Online harf seçimi ekranı:** Maç başında her iki oyuncudan 1'er harf alınır (harf seçici arayüz). Sistem çözülebilir çift garanti eder.

**Akış (online):** Her oyuncu harf seçer → kriter belirir → ilk geçerli cevabı veren kazanır → 30 sn'de cevap yoksa beraberlik. Tek oyunculuda sistem 2 harf verir.

**Tasarım notu:** Harf seçici hızlı ve net olmalı; "B ile başlayıp O ile biten" kuralı görsel olarak çok açık sunulmalı.

---

### 8.9. Bayrak XI (Bayraklarla İlk 11)
**Amaç:** Mevkilere yerleştirilmiş uyruk bayraklarından takımı/kadroyu bulmak.

**Ana öğeler:**
- **Saha dizilimi:** Mevkilerde oyuncu yerine **uyruk bayrakları**.
- **Tahmin giriş alanı:** Takım adı (autocomplete).
- **Hak göstergesi:** 3 hak.

**Akış:** Bayraklı kadroyu incele → takımı tahmin et → 3 hakta bulmaya çalış.

**Online vs Tek oyunculu:** Online'da ilk bilen kazanır (yine 3 hak); tek oyunculuda 3 hak.

**Tasarım notu:** Saha + 11 bayrak küçük ekranda okunaklı olmalı; bayraklar net, mevki etiketleri görünür.

---

### 8.10. Zincir Oyunu (Oyuncu–Takım Örgüsü, yalnızca online, çok oyunculu)
**Amaç:** Sırayla oyuncu↔takım zinciri kurmak; tekrar/boş bırakan elenir.

**Ana öğeler:**
- **Katılımcı listesi:** Tüm oyuncular + kimin sırası (vurgulu) + elenenler (soluk).
- **Zincir geçmişi:** Son söylenenler dikey/yatay liste (tekrar kontrolü için görünür).
- **Aktif istem:** "Messi'nin oynadığı bir takım söyle" gibi net yönerge.
- **Giriş alanı + 15 sn sayaç.**

**Akış:** Sıra sende → istemi karşıla (geçerli + tekrarsız) → süre dolarsa/geçersizse elenirsin → son kalan kazanır.

**Tasarım notu:** Çok oyunculu sıra akışı net olmalı; "sıra sana geliyor" uyarısı (oyuncu dikkatini kaybedebilir). Elenme anı dramatik ama nazik.

---

### 8.11. Oyun Ekranları Ortak Kontrol Listesi
Tasarımcı her oyun ekranında şunları sağlamalı:
- [ ] Mod adı / tur bilgisi
- [ ] Süre (varsa) — renk körü uyumlu
- [ ] Hak/can (varsa)
- [ ] Skor / hedef / ilerleme
- [ ] Rakip(ler) durumu (online)
- [ ] Giriş/aksiyon alanı (autocomplete tutarlı)
- [ ] Doğru/yanlış geri bildirimi (renk + ikon)
- [ ] Çıkış (onaylı)
- [ ] Yükleniyor / bağlantı kopması durumu
- [ ] "Nasıl oynanır" erişimi

---

## 9. Rekabet Ekranları (Lig, Lider Tabloları)

### 9.1. Lig Ekranı
**Amaç:** Oyuncunun mevcut haftalık lig durumunu ve terfi/düşme yarışını göstermek.
- Mevcut lig tier'ı (Bronz…Efsane) — renk + ikon + ad.
- **Sıralama listesi:** Lig grubundaki oyuncular, puan/rating ile sıralı; kullanıcının satırı vurgulu.
- **Terfi / düşme barajları:** Listede görsel ayraçlar — "buradan yukarısı terfi (ilk %10)", "buradan aşağısı düşer (son %10)", ortada "kalır". Renk + ikon + etiket.
- Hafta sonuna kalan süre (geri sayım).
- 1.lik Gems ödülü göstergesi.

### 9.2. Lider Tabloları
Sekmeli ekran: **Global · Ülke · Arkadaşlar · Mod Bazlı**.
- Her satır: sıra, avatar, isim, level/rating veya moda özel skor.
- Kullanıcının kendi sırası her zaman görünür ("sen buradasın" sabit satır, çok aşağıda olsa bile).
- Global için sayfalama + "yakınımdakiler" görünümü.
- **Arkadaşlar sekmesi** özellikle önemli (yakın çevre rekabeti).
- Boş durum (arkadaş yok → "arkadaş ekle" CTA).

---

## 10. Ekonomi ve Market Ekranları

### 10.1. Market (Ana)
Sekmeli/bölümlü: **Gems · Chip · Avatar · Takviyeler · Battle Pass**.

### 10.2. Gems Paketleri (IAP)
- Paket kartları: miktar, fiyat (yerel para), "en popüler/en avantajlı" rozetleri, ilk alım bonusu.
- Satın alma akışı platform (Apple/Google) ödeme ekranına bağlanır; sonuç (başarılı/iptal/hata) geri bildirimi.

### 10.3. Chip Paketleri
- Gems veya doğrudan para ile Chip; "iflas koruması" kısayolu da burada olabilir.

### 10.4. Avatar Mağazası
- Parça kategorileri (forma, atkı, krampon, şapka, arka plan, çerçeve).
- Her parça: önizleme (avatar üzerinde), fiyat (Gems/Chip), nadirlik etiketi (Yaygın/Nadir/Efsanevi), kilitli/sahip durumları.
- Efsanevi parçalar "yalnızca ödül" → satın alınamaz, nasıl kazanılacağı belirtilir.
- Deneme/önizleme: parçayı avatarın üzerinde canlı görme.

### 10.5. Takviyeler
- 2× XP / 2× Chip süreli boost kartları: süre, fiyat (Gems), aktif boost geri sayımı.

### 10.6. Battle Pass / Sezon Geçişi (Faz 3)
- İki paralel ödül yolu (ücretsiz / premium), XP ilerleme çubuğu, sıradaki ödüller, kalan sezon süresi, satın alma CTA.

### 10.7. Satın Alma Onayı & Geri Bildirim
- Tüm harcamalar (Gems/Chip) onay ister; bakiye yetersizse "al" kısayolu.
- Başarılı satın almada tatmin edici animasyon; hata durumları net.

---

## 11. Profil, Avatar, Başarımlar

### 11.1. Profil Özeti
- Büyük avatar + isim + level + lig rozeti + rating.
- Vitrin: öne çıkarılan 3 başarım rozeti.
- Hızlı istatistik (oynanan maç, galibiyet oranı, en iyi mod).
- "Avatarı Düzenle", "İstatistikler", "Başarımlar", "Ayarlar" girişleri.

### 11.2. Avatar Özelleştirme
- Canlı avatar önizleme (büyük).
- Kategori sekmeleri + sahip olunan parçalar grid'i.
- Parça seçince anında avatara uygulanır; kaydet/iptal.
- Sahip olunmayan parça → kilit + "Market'te edin".

### 11.3. İstatistikler
- Genel + mod bazlı (oynanan, kazanılan, oran, en iyi skorlar, rekorlar).
- Grafiksel özet (tasarımcı sade tutmalı).

### 11.4. Başarımlar
- Kategoriler (İlerleme, Beceri, Mod ustalığı, Rekabet, Sadakat, Sosyal).
- Her başarım: ikon/rozet, ad, açıklama, ilerleme (örn. "37/50"), kademe (Bronz→Platin), ödül.
- Kilitli/açık durumlar; açılınca kutlama.

---

## 12. Sosyal Ekranlar

### 12.1. Arkadaş Listesi
- Arkadaşlar: avatar, isim, online/level/lig; "düelloya davet" aksiyonu.
- Boş durum → "Arkadaş ekle" CTA.

### 12.2. Arkadaş Ekle / Davet
- Kullanıcı adı/etiket ile arama; davet linki/kodu paylaşımı.
- Gelen istekler (kabul/ret).

### 12.3. Özel Oda Kur / Katıl
- Mod + (opsiyonel) bahis seç → oda oluştur → davet linki/kod paylaş.
- Koda/linke katılma akışı.
- Oda lobisi: katılanlar listesi, "başlat" (kurucu).

### 12.4. Piramit Akışı (Keşfet)
- Yayınlanan piramit kartları akışı (özne + piramit önizleme + katıl/beğeni sayısı).
- Karta dokun → detay + katıl/katılma + topluluk dağılımı.
- Kendi piramidini paylaşma kısayolu.

---

## 13. Ayarlar ve Sistem Ekranları

### 13.1. Ayarlar (Ana)
- **Hesap:** Bağlı giriş yöntemleri, e-posta, çıkış yap, hesap sil (veri silme — KVKK/GDPR).
- **Ses:** Müzik / SFX / Haptik ayrı açma-kapama + seviye.
- **Erişilebilirlik:** Renk körü modu (alternatif palet), yazı boyutu, (varsa) süre esnekliği (tek oyunculu).
- **Bildirimler:** Tür bazlı açma-kapama.
- **Dil:** Dil seçimi.
- **Tema:** Açık/Koyu/Sistem (varsa).
- **Yasal/Destek:** Gizlilik politikası, kullanım şartları, destek/iletişim, SSS, sürüm bilgisi.

### 13.2. Bildirimler / Inbox (opsiyonel)
- Sistem mesajları, ödüller, davetler, duyurular.

---

## 14. Ekran Durumları (States) — Genel Kurallar

Her ekran/bileşen için tasarlanması gereken durumlar:

| Durum | Ne zaman | Tasarım gereği |
|-------|----------|----------------|
| **Yükleniyor** | Veri gelirken | Skeleton (tercih) veya spinner; içerik geldikçe kademeli göster |
| **Boş (empty)** | Liste boş (arkadaş yok, başarım yok) | Açıklayıcı görsel + tek net CTA |
| **Hata** | İstek başarısız | Nazik mesaj + "Tekrar dene" |
| **Bağlantı yok** | İnternet kopuk | Global banner/ekran; online özellikler pasif; tek oyunculu da sunucuya bağlı olduğundan uyarı |
| **İzin reddedildi** | Bildirim vb. | Ayarlara yönlendiren açıklama |
| **Yetersiz bakiye** | Chip/Gems az | İlgili market kısayolu |
| **Başarı/onay** | İşlem tamam | Kısa olumlu geri bildirim (toast/animasyon) |
| **Oyun: kazandın/kaybettin/berabere** | Maç sonu | §7.5 sonuç ekranı |
| **Oyun: bağlantı koptu** | Online kopma | Yeniden bağlanma denemesi + hükmen sonuç uyarısı |

> **Bağlantı notu:** Tek oyunculu modlar da sunucuya bağlıdır. "İnternetsiz oynanabilir" izlenimi verilmemeli; bağlantı yoksa uygun uyarı gösterilmeli.

---

## 15. Mikro-etkileşimler ve Animasyon

Tasarımcının tanımlaması beklenen tutarlı hareket dili:
- **Doğru cevap:** yeşil + ✓ + kısa pozitif animasyon (örn. hücreye/sıraya yerleşme).
- **Yanlış cevap:** kırmızı + ✗ + nazik sarsıntı/uyarı (cezalandırıcı değil).
- **Süre baskısı:** son saniyelerde sayaç nabız/renk + (opsiyonel) haptik.
- **Ödül akışı:** Chip/XP sayaca akma, level bar dolumu, level-up patlaması.
- **Terfi/düşme:** lig değişimi kutlaması veya nazik düşüş bildirimi.
- **Başarım açılışı:** rozet belirme animasyonu.
- **Geçişler:** ekranlar arası tutarlı, hızlı (oyunu yavaşlatmayan) geçişler.
- **Buton geri bildirimi:** her dokunulabilir öğe basılı durumda tepki vermeli.

İlke: Animasyon **bilgilendirir ve ödüllendirir**, ama akışı yavaşlatmaz. Atlanabilir/kısa olmalı (tekrar eden oturumlar).

---

## 16. Erişilebilirlik Kontrol Listesi

- [ ] **Renk + ikon/şekil çift kodlama:** doğru/yanlış, yeşil/kırmızı, oyuncu sembolleri, lig renkleri — hiçbiri yalnızca renge dayanmaz.
- [ ] **Piramit** ve **Tic-Tac-Toe** durumları ikon/desenle de ayrışır.
- [ ] **Renk körü modu** (alternatif palet) ayarlarda.
- [ ] **Kontrast:** WCAG AA (4.5:1 / 3:1).
- [ ] **Yazı boyutu** ölçeklenebilir; metinler taşmadan uyum sağlar.
- [ ] **Dokunma hedefleri** ≥ ~44×44 pt.
- [ ] **Ses bağımsızlığı:** kritik bilgi sesle değil görselle de verilir.
- [ ] **Süre esnekliği** (tek oyunculu): uzatılabilir/kapatılabilir seçenek.
- [ ] **Hareket azaltma (reduce motion):** animasyonları azaltan sistem ayarına saygı.
- [ ] **Ekran okuyucu (opsiyonel/ileri):** önemli öğelerde etiketler.

---

## 17. Metin / Mikrocopy İhtiyaçları

Tasarımcının (veya UX yazarının) yazması gereken metin alanları — **dil: Türkçe**, kısa, net, sıcak ama rekabetçi ton:
- Buton etiketleri (Oyna, Tekrar Oyna, Onayla, İptal, Topla…).
- Mod adları + tek cümlelik açıklamalar (11 mod).
- Her mod için **tutorial adımları**.
- "Nasıl oynanır" kısa açıklamaları.
- Boş durum / hata / bağlantı mesajları.
- Onay diyalogları (çıkış, satın alma, hesap silme).
- Sonuç ekranı başlıkları (zafer/yenilgi/berabere).
- Bildirim metinleri (streak, davet, lig).
- Yasal/gizlilik kısa açıklamaları.

> Not: Çoğul/yerelleştirme için metinler değişken-dostu yazılmalı (örn. "{n} Chip kazandın").

---

## 18. Responsive ve Cihaz Notları

- **Öncelik:** Mobil dikey (portrait). Çoğu mod tek el dikey kullanım için tasarlanmalı.
- **Ekran aralığı:** Küçük telefonlardan büyük telefonlara; güvenli alanlar (çentik, home indicator) korunmalı.
- **Yoğun ekranlar:** Tic-Tac-Toe (4×4 + başlıklar), Kadro Kurma (11 slot), Zincir (çok oyuncu) küçük ekranda en zorlu testler → bunlar önce çözülmeli.
- **Tablet/Web (Faz 4):** Sistem baştan esnek ızgarayla kurulursa sonraki uyarlama kolaylaşır (zorunlu değil ama önerilir).
- **Yatay (landscape):** Gerekli değil; istenirse oyun ekranları hariç dikey kilitlenebilir.

---

## 19. Tasarımcıdan Beklenen Teslimatlar

1. **Tasarım Sistemi (Design System) dosyası:** renk token'ları, tipografi, spacing, ikon seti, bileşen kütüphanesi (tüm durumlarıyla), açık+koyu tema.
2. **Bilgi mimarisi & akış şemaları:** §3 IA'nın görselleştirilmiş hali + ana kullanıcı akışları (onboarding, oyun oturumu, satın alma).
3. **Wireframe'ler (düşük çözünürlük):** tüm ekranların yapısal taslakları (önce onay için).
4. **Yüksek çözünürlüklü tasarımlar (hi-fi):** tüm ekranlar, tüm önemli durumlar (§14).
5. **11 oyun ekranı** — her biri tüm durumlarıyla (boş/dolu/doğru/yanlış/süre bitti/kazandı/kaybetti).
6. **Etkileşimli prototip:** en az ana akış (onboarding → oyna → sonuç) ve 2-3 temsili mod.
7. **Mikro-etkileşim/animasyon spesifikasyonları** (§15) — tetik, süre, easing notları.
8. **Erişilebilirlik raporu:** §16 kontrol listesinin karşılandığının gösterimi.
9. **Geliştirici teslim paketi (handoff):** ölçüler, token'lar, asset export, redline/spec.
10. **Mikrocopy dökümü** (§17) — Türkçe, yerelleştirmeye uygun.

---

## 20. Tasarım Önceliği (MVP → Sonra)

> GDD yol haritasıyla uyumlu. Tasarımcı bu sırayla ilerlemeli.

### Faz 1 — MVP (önce tasarlanacak)
- Tasarım sistemi temeli (token + temel bileşenler + autocomplete).
- Onboarding + Giriş/Kayıt.
- Ana Menü, Mod Seçim, Oda Seçim, Eşleştirme, Sonuç.
- **3 oyun ekranı:** Kariyer İzi (8.6), İlk 10 (8.4), Kesişim Düellosu (8.5).
- Bu 3 mod için tutorial.
- Temel Lig/Sıralama, temel Profil, temel Ayarlar.
- Erişilebilirlik temeli (renk körü çift kodlama).

### Faz 2
- Market (Gems/Chip/Avatar/Takviye), Avatar özelleştirme.
- Tam Lig + terfi/düşme görselleri, Lider Tabloları (global/arkadaş).
- Başarımlar.
- Ses/animasyon spesifikasyonlarının zenginleştirilmesi.
- +4 oyun ekranı: Tic-Tac-Toe (8.3), Bayrak XI (8.9), Harf Düellosu (8.8), Kadro Kurma (8.2).

### Faz 3
- Sosyal (arkadaş, özel oda), Piramit + akış, Battle Pass.
- +3 oyun ekranı: Piramit (8.7), Zincir (8.10), Kariyer İstatistiği Avı (8.1).
- UGC moderasyon arayüzleri.

---

## 21. Tasarımcının Karar Vermesi Gerekenler

Bu doküman *ne* gerektiğini söyler; aşağıdakiler tasarımcının yaratıcı/uzmanlık alanına bırakılmıştır:
1. **Görsel kimlik:** renk paleti, tipografi, marka hissi (saha temalı mı, daha soyut mı?).
2. **Saha metaforu kullanımı:** Kadro Kurma ve Bayrak XI'de gerçek saha görseli mi, soyut dizilim mi?
3. **Navigasyon detayı:** alt sekme + üst bar düzeninin tam yerleşimi.
4. **Animasyon dili ve yoğunluğu** (hız ↔ gösteriş dengesi).
5. **Tic-Tac-Toe ve Kadro Kurma'nın küçük ekran çözümü** (en zorlu yerleşimler).
6. **Jenerik temsiller:** Lisans alınana kadar oyuncu/kulüp/bayrak için görsel sistem (silüet, baş harf rozetleri, jenerik bayraklar).
7. **Paylaşılabilir piramit kartı** tasarımı (sosyal medya formatı).

### Açık ürün kararları (GDD'den devreden — tasarımı etkileyebilir)
- **İsim/marka:** henüz belirlenmedi → logo/marka tasarımı buna bağlı.
- **Veri kaynağı & lisans:** gerçek logo/foto kullanılıp kullanılamayacağı netleşince görsel zenginlik değişir; bu yüzden tasarım **jenerik temsil varsayımıyla** başlamalı, sonradan zenginleştirilebilir olmalı.

---

*Doküman sonu — UI/UX Tasarım Dokümanı v1.0. Kaynak: GDD v1.1. Görsel kimlik ve marka kararları tasarımcıya bırakılmıştır; bu doküman kapsam, davranış ve eksiksizlik içindir.*
