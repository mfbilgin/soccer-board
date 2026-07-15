# Futbol Tahmin Oyunu — Oyun Tasarım Dokümanı (GDD)

| Alan | Bilgi |
|------|-------|
| Doküman Adı | Futbol Tahmin Oyunu — Game Design Document |
| Versiyon | 1.1 (Taslak) |
| Durum | İnceleme için hazır |
| Tarih | 28 Haziran 2026 |
| Çalışma Adı | *(Belirlenecek — bkz. §1.6)* |
| Platform | iOS, Android (Faz 2: Web) |
| Tür | Trivia / Bilgi yarışması · Futbol · Casual–Competitive · Multiplayer |

> **Not:** Bu doküman, sağladığınız oyun şemasını temel alır ve onu eksiksiz bir tasarım dokümanına dönüştürür. Şemada açıkça belirtilmeyen ancak ürünün çalışması için zorunlu olan kararlar (eşleştirme, hile önleme, veri kaynağı, ekonomi dengesi, kenar durumları vb.) "Tasarım Kararı" olarak işaretlenmiş ve gerekçelendirilmiştir. Bunlar tartışmaya açıktır.

---

## İçindekiler

1. Yönetici Özeti ve Vizyon
2. Temel Oyun Döngüsü (Core Loop)
3. Oyun Modları (Detaylı)
4. Ekonomi Sistemi (Gems & Chip)
5. İlerleme Sistemleri (Level / XP / Başarımlar)
6. Rekabet Sistemi (Rank / Elo / Ligler / Lider Tabloları)
7. Avatar ve Özelleştirme
8. Online Altyapı (Eşleştirme, Hesap, Sosyal, Hile Önleme, Moderasyon)
9. Veri Modeli ve İçerik Kaynağı
10. Kullanıcı Arayüzü, Sanat Yönetimi, Ses ve Erişilebilirlik
11. Onboarding, Tutorial ve Tutundurma (Retention)
12. Monetizasyon
13. Teknik Mimari
14. KPI'lar ve Analitik
15. Geliştirme Yol Haritası ve MVP Kapsamı
16. Yasal Uyumluluk ve Regülasyon
17. Riskler ve Önlemler
18. Açık Sorular ve Kararlar
19. Sözlük (Glossary)

---

## 1. Yönetici Özeti ve Vizyon

### 1.1. Tek Cümlelik Tanım
Futbol meraklılarının bilgisini hızlı, rekabetçi mini oyunlarla test eden; çevrimiçi (çok oyunculu) ve tek oyunculu oynanabilen, ekonomi ve lig sistemi olan bir mobil futbol tahmin oyunu.

### 1.2. Vizyon
Futbol bilgisini "sosyal bir spora" dönüştürmek. Oyuncular yalnızca tek başına çözmekle kalmaz; arkadaşlarına ve dünyadaki diğer oyunculara karşı yarışır, lig atlar, koleksiyon yapar ve günlük olarak geri döner.

### 1.3. Hedef Kitle
- **Birincil:** 16–35 yaş, futbolu yakından takip eden, transfer/kariyer geçmişi gibi detayları bilen "hardcore" taraftarlar.
- **İkincil:** Casual futbol izleyicileri; bayrak/ilk 11 gibi görsel ve kolay modlarla giriş yapar.
- **Coğrafya:** Önce TR pazarı, ardından futbol kültürü güçlü pazarlar (TR, MENA, LatAm, Güney Avrupa).

### 1.4. Benzersiz Değer Önerisi (USP)
- Tek bir uygulamada **11 farklı oyun modu** (rakipler genellikle 1–2 mod sunar).
- Hem **çevrimiçi rekabet** hem **tek oyunculu pratik** aynı modlarda.
- Bilgi temelli **gerçek beceri ekonomisi** (şans değil, bilgi kazandırır).

### 1.5. Platform ve Teknik Hedefler
- **MVP:** iOS + Android (native veya Flutter/Unity — bkz. §13).
- **Tüm modlar (tek oyunculu dahil) sunucuya bağlıdır; oyun verisi cihazda tutulmaz.** Çevrimiçi (çok oyunculu) modlar ayrıca düşük gecikmeli gerçek zamanlı bağlantı gerektirir.
- Hedef cihaz: Orta segment akıllı telefonlar (3 yıl öncesine kadar).

### 1.6. Tasarım Kararı — İsim
Şemada isim yok. Aday yönler: "kariyer/transfer bilme" ve "bilgi düellosu" temaları öne çıkıyor. Pazarlama aşamasında belirlenmeli; bu doküman boyunca "Oyun" denmektedir.

### 1.7. Tasarım İlkeleri (Pusula)
Tüm tasarım kararları bu ilkelere göre değerlendirilir:
1. **Bilgi ödüllendirilir, şans değil.** Ekonomi ve puanlama beceriyi yansıtmalı.
2. **Hızlı oturum.** Her tek el 30–120 saniyede bitmeli; "bir el daha" hissi.
3. **Adil ücretsiz oyun (F2P).** Para harcamayan oyuncu da rekabet edebilir; para yalnızca hız/kozmetik/konfor sağlar (pay-to-win değil).
4. **Tek oyunculu mod her zaman değerlidir.** Oyuncu rakip beklemeden, kendi hızında pratik yapar ve XP kazanır (mod sunucuya bağlıdır; veri cihazda tutulmaz).

---

## 2. Temel Oyun Döngüsü (Core Loop)

### 2.1. Oturum Döngüsü (Session Loop)
```
Uygulamayı aç
   → Günlük streak/ödül kontrolü
      → Mod seç
         → (Online) Oda/ücret seç → Eşleştirme → Maç → Sonuç → Ödül (Chip/XP/Rating)
         → (Tek Oyunculu) Mod oyna → Sonuç → Ödül (XP)
      → Level/Rank ilerlemesi güncellenir
   → Market / Avatar / Lig tablosu incele
   → Çık
```

### 2.2. Meta Döngü (Uzun Vade)
```
Günlük oyna → XP & Rating kazan → Level atla & Lig yüksel
   → Ödül (Gems, avatar parçaları) → Avatarı geliştir & Chip ile yüksek odalarda oyna
   → Sezon sonu lig ödülü → Yeni sezona daha güçlü başla
```

### 2.3. Üç Para Birimi / İlerleme Eksenleri
| Eksen | Birim | Anlamı | Kaynağı |
|-------|-------|--------|---------|
| Premium ekonomi | **Gems** | Nadir, değerli; konfor/hız satın alır | IAP, lig 1.liği, streak |
| Yumuşak ekonomi | **Chip** | Oda bahisleri; oyunla kazanılır | Oda kazançları, Gems takası |
| Beceri/Statü | **XP / Rating** | İlerleme ve sıralama | Her oyun |

Bu üç eksen birbirini besler ama birbirinin yerine geçmez — sağlıklı F2P ekonomisinin temeli budur.

---

## 3. Oyun Modları (Detaylı)

Her mod için: **Tanım · Akış · Kazanma Koşulu · Puanlama · Online/Tek Oyunculu farkları · Kenar durumları · UI notları** verilir.

### Ortak Online Kuralları (Tüm modlar için geçerli)
- **Oda ücreti:** Oyuncu odaya girerken Chip öder. Ödül havuzu = tüm girenlerin ücreti. Kazanan havuzun **%90'ını** alır; **%10 sistem kesintisidir (rake)**.
- **Beraberlik / kazanan yok:** Hiç kimse kazanma koşulunu sağlamazsa, oda ücretleri iade edilir (rake alınmaz). *(Tasarım Kararı: oyuncu güveni için.)*
- **Bağlantı kopması:** Oyuncu maçtan kopar ve süre içinde dönmezse, hükmen kaybeder; el devam ediyorsa rakibi kazanmış sayılır. (Bilinçli "rage-quit" sömürüsünü önler.)
- **Zamanlayıcı:** Tüm tur bazlı modlarda sunucu otoritesidir; istemci yalnızca gösterir.

---

### 3.1. Hedef Tutturma Modu — "Kariyer İstatistiği Avı"
> *Şemadaki: "x adet futbolcuyla x ligde/tüm zamanlarda x maç/gol/asist/kart sayısına ulaş."*

**Tanım:** Oyunculara bir **hedef değer** verilir (örn. "La Liga'da toplam 500 gol") ve herkesin gireceği **sabit bir futbolcu sayısı** belirlenir. Her oyuncu, bu sabit sayıda futbolcuyu seçerek istatistik toplamını **hedefe olabildiğince yaklaştırmaya** çalışır. Hedefe en yakın olan oyuncu kazanır.

**Parametreler (oyun başında belirlenir):**
- Girilecek futbolcu sayısı (herkes için sabit, örn. 3 futbolcu)
- Kapsam: belirli bir lig **veya** "tüm zamanlar/tüm kariyer"
- Metrik: maç · gol · asist · sarı kart · kırmızı kart
- Hedef değer

**Akış:**
1. Sistem hedefi ve sabit futbolcu sayısını gösterir: *"3 futbolcu ile, La Liga'da, toplam 500 gol hedefine en yakın ol."*
2. Oyuncu sabit sayıda futbolcuyu sırayla yazar/seçer.
3. Her geçerli futbolcunun ilgili istatistiği toplanır ve toplam, hedefe olan uzaklığıyla (örn. "+12" / "−40") gösterilir.
4. Belirlenen futbolcu sayısı dolduğunda oyuncunun eli biter.

**Kazanma Koşulu:**
- **Online:** Tüm oyuncular sabit sayıda futbolcusunu girer; toplamı hedefe **en yakın** olan kazanır. Hedefe **eşit uzaklıkta** (alt/üst fark etmeksizin mutlak uzaklık eşitse) birden çok oyuncu varsa **berabere** biter (oda ücreti iadesi, bkz. ortak online kuralları).
- **Tek Oyunculu:** Yarışma yok; oyuncu sabit sayıda futbolcuyla hedefe en yakın toplamı (ideal olarak tam isabet) yakalamaya çalışır, kendi rekorunu kırar.

**Puanlama (Online):** Hedefe ne kadar yakınsanız o kadar çok XP/Rating; tam isabet en yüksek ödülü verir.

**Kenar durumları:**
- Aynı futbolcu iki kez yazılamaz.
- Yazılan oyuncu kapsamla uyumsuzsa (örn. La Liga'da hiç oynamamış) geçersiz sayılır, hata gösterilir, hak yanmaz.
- İmla/eşadlılık: otomatik tamamlama (autocomplete) ile resmi isim seçtirilir (bkz. §9.4).

---

### 3.2. En İyi Kadro Kurma — "Hayalindeki Sınırlı XI"
> *Şemadaki: "en (genç/uzun) kadroyu kur. Her oyuncu farklı bir takımda aktif olmalı."*

**Tanım:** Oyuncu, verilen kritere göre **en uç** (en genç / en uzun / vb.) bir ilk 11 kurar. Kadro **1-4-3-3** dizilimiyle oluşturulur ve mevkiler dört genel rol üzerinden girilir: **Kaleci (1) · Defans (4) · Ortasaha (3) · Forvet (3)**. **Kısıt:** her futbolcu **farklı bir takımda hâlihazırda aktif** olmalıdır (örn. bir defans oyuncusu Milan'da aktifse, kadroda başka hiçbir mevkide Milan'lı oyuncu olamaz).

**Parametreler:**
- Optimize edilecek kriter: en genç toplam yaş / en uzun toplam boy / (genişletilebilir: en pahalı, en çok asistli vb.)
- Dizilim sabit: **1-4-3-3** (1 Kaleci, 4 Defans, 3 Ortasaha, 3 Forvet).

**Akış:**
1. Sistem kriteri verir; dizilim 1-4-3-3 olarak sabittir.
2. Oyuncu her role (Kaleci / Defans / Ortasaha / Forvet), o rolde oynayan ve **kullanılmamış bir takımdan** aktif futbolcu yerleştirir.
3. Sistem toplam skoru hesaplar (örn. yaş toplamı/ortalaması).

**Kazanma Koşulu:**
- **Online:** En iyi toplam skora sahip kadro kazanır (en küçük yaş / en büyük boy toplamı).
- **Tek Oyunculu:** Kişisel rekor / kriteri aşma.

**Kenar durumları:**
- Takım benzersizliği zorunlu: aynı kulüpten iki oyuncu kullanılamaz (kontrol edilir).
- "Aktif" tanımı veri tarihine bağlıdır → veri tabanı "current_club" alanıyla güncel tutulmalı (bkz. §9).
- Rol uyumu, dört genel kategori üzerinden değerlendirilir: futbolcunun veritabanındaki mevkisi Kaleci/Defans/Ortasaha/Forvet rollerinden hangisine giriyorsa o role yerleştirilebilir (örn. her tür stoper/bek "Defans" sayılır).

---

### 3.3. Futbol Tic-Tac-Toe (4×4 Izgara)
> *Şemadaki: 4×4 matris, iki tür.*

**Tanım:** Klasik "futbol grid" oyununun 4×4 versiyonu. Satır ve sütun başlıkları takım veya oyunculardan oluşur; kesişimler doldurulur.

**İki Tür:**
- **Tür A (Takım × Takım):** İlk satır ve ilk sütun **takımlardan** oluşur. Kesişime, **her iki takımda da oynamış** bir futbolcu yazılır.
- **Tür B (Oyuncu × Oyuncu):** İlk satır ve ilk sütun **oyunculardan** oluşur. Kesişime, **her iki oyuncunun da oynadığı** bir takım yazılır.

**Izgara yapısı:** 4×4 → ilk satır + ilk sütun başlık (1 köşe boş/etiket), kalan **3×3 = 9 hücre** doldurulur.

**Akış (Online, 2 kişi):**
1. Sistem başlıkları üretir (çözülebilir olduğu garanti edilir — bkz. kenar durumları).
2. Oyuncular sırayla bir hücre seçip cevap yazar.
3. Doğru cevap → o hücre oyuncunun rengiyle **ve sembolüyle** işaretlenir (renk körlüğü için çift kodlama — bkz. §10.6).
4. Yanlış → sıra rakibe geçer (hücre boş kalır).

**Kazanma Koşulu:**
- Yatay, dikey veya çapraz **3'lü dizi** tamamlayan oyuncu kazanır.
- **Hiç 3'lü dizi oluşmazsa** (tüm hücreler dolar ya da kilitlenirse) el sonuçsuz biter; **yeni bir matris gelir** ve oyun, biri 3'lü dizi yapana kadar devam eder.
- **Tek Oyunculu:** Tek oyuncu tüm 9 hücreyi doldurmaya çalışır (süre/hata limitiyle).

**Benzersizlik kuralı:** Aynı futbolcu/takım ızgarada bir kez kullanılabilir (zorluk için; opsiyonel ayar).

**Kenar durumları (KRİTİK):**
- **Çözülebilirlik garantisi:** Üretilen her başlık kombinasyonu için en az 1 geçerli cevap **var olmalı**. Sistem ızgarayı veritabanından geri-üretir (önce çözümleri bulur, sonra başlıkları koyar).
- **Doğrulama:** Cevap, kesişim koşulunu sağlıyor mu kontrol edilir (oyuncu A & B'de oynamış mı).
- Aynı anda iki oyuncu farklı hücreyi seçebilir mi? *(Tasarım Kararı: sıra tabanlı, çakışmayı önler.)*

---

### 3.4. En Çok Gol/Asist Yapan 10 Futbolcu — "İlk 10 Listesi"
> *Şemadaki: 10 kutucuk, ilk 3 dolu, 3 yanlış hakkı.*

**Tanım:** Bir ligde/tüm zamanlarda bir metrikte (gol veya asist) **ilk 10** futbolcu sıralı kutularda gizlidir. İlk 3 açık başlar; oyuncu kalan 7'yi tahmin eder.

**Akış:**
1. Sistem başlık verir: *"Süper Lig tüm zamanlar en çok gol — İlk 10."*
2. 10 kutu alt alta; ilk 3 dolu gelir.
3. Oyuncu bir isim yazar; isim listede varsa **doğru sırasına** yerleşir.
4. **3 yanlış hakkı** vardır; biten her hak bir "can" yakar.

**Online:**
- Oyuncular **sırayla** tahmin yapar.
- **Puanlama:** Bilinen futbolcunun **sıra numarası kadar puan** kazanılır. Yani 10. sıradaki futbolcuyu bilen 10 puan, 9. sıradakini bilen 9 puan... 1. sıradakini bilen 1 puan alır. Alt sıralar (daha az gol/asist, daha az bilinen oyuncular) daha zor olduğu için daha çok puan getirir.
- En çok puanı alan kazanır.

**Tek Oyunculu:** Yarışma yok; oyuncu tüm listeyi 3 hata hakkıyla açmaya çalışır.

**Kenar durumları:**
- Yanlış sıra ama doğru oyuncu? *(Tasarım Kararı: oyuncu yalnızca ismi yazar; sistem doğru sıraya koyar. Sıra tahmini istenmez — sürtünmeyi azaltır.)*
- Eşadlılık → autocomplete.
- Liste güncelliği: "tüm zamanlar" listeleri verinin doğruluğuna bağlı (bkz. §9).

---

### 3.5. İki Takım/Ülkeden Futbolcu Bul — "Kesişim Düellosu"
> *Şemadaki: online; Takım-Ülke ve Takım-Takım.*

**Tanım:** İki kriterin kesişiminde yer alan bir futbolcuyu ilk bulan kazanır.

**İki Tür:**
- **Tür 1 (Takım-Ülke):** Bir kriter takım, diğeri ülke. Cevap: o **ülke uyruklu** ve o **takımda kariyerinde oynamış** bir futbolcu.
- **Tür 2 (Takım-Takım):** İki takımda da oynamış bir futbolcu.

**Akış (Online, gerçek zamanlı):**
1. Sistem iki kriteri gösterir: *"Brezilya + AC Milan."*
2. Her iki oyuncu da aynı anda tahmin etmeye çalışır.
3. İlk geçerli cevabı giren kazanır.

**Kazanma Koşulu:** İlk doğru cevap.

**Kenar durumları:**
- Çözülebilirlik garantisi (en az 1 cevap var).
- Süre limiti: kimse bulamazsa → beraberlik (ücret iadesi).
- Çoklu doğru cevap kabul edilir; ilk geçerli yeterli.

---

### 3.6. Transfer/Kariyer Geçmişinden Futbolcu Tahmini — "Kariyer İzi"
> *Şemadaki: Man Utd → Real → Juventus → Man Utd → Al-Nassr örneği.*

**Tanım:** Oyuncuya bir **kariyer/transfer dizisi** verilir; oyuncu futbolcuyu tahmin eder. Takım adlarının yanında **yıl** opsiyonel verilebilir (zorluk ayarı).

**Akış:**
1. Sistem kariyer zincirini gösterir (ilk başta kısmen gizlenebilir / ipucu kademeli açılabilir — bkz. zorluk).
2. Oyuncu futbolcu adını tahmin eder.

**Online:** İlk doğru bilen kazanır.
**Tek Oyunculu:** **5 tahmin hakkı** vardır.

**Zorluk seçenekleri (Tasarım Kararı):**
- Kolay: yıllar gösterilir + tüm kulüpler.
- Zor: yıl yok; bazı kulüpler "???" gizli, her yanlışta bir kulüp açılır (tek oyunculuda hak başına ipucu).

**Kenar durumları:**
- Loan (kiralık) dönemleri zincire dahil mi? *(Tasarım Kararı: dahil, "(loan)" etiketiyle; bilgili oyuncuya ipucu olur.)*
- Eşadlılık → autocomplete; doğum yılı disambiguation.

---

### 3.7. Top 50/25/10/5/3/1 Piramidi — "Sıralama Görüşü"
> *Şemadaki: yarışma değil, eğlence/fikir belirtme modu.*

**Tanım:** Bir oyuncu ya da takımın, tarihin en iyileri sıralamasında nereye kadar girdiğini bir **piramide** yerleştirme. Katmanlar aşağıdan yukarı: **50 → 25 → 10 → 5 → 3 → 1**.

**Akış:**
1. Kullanıcı bir özne seçer (örn. "Zidane").
2. Her katman için "evet bu sıralamada var" / "hayır yok" der.
3. İlk "evet"lerde katman **yeşil**; **ilk "hayır"dan sonra** üst katmanların hepsi **kırmızı** olur. (Renk körlüğü için katmanlar renk + ikon/desen ile çift kodlanır — bkz. §10.6.)
   - Örnek: Zidane top 50 ✅ → top 25 ✅ → top 10 ❌ → üstü kırmızı.
4. Tamamlanan piramit, kullanıcı onayıyla **diğer oyunculara açık olarak yayınlanır**.

**Sosyal katman (Tasarım Kararı — bu modun değerini katlar):**
- Yayınlanan piramitlere diğer oyuncular **katılma/beğeni/itiraz** (agree/disagree) verebilir.
- Toplu görüş bir "topluluk piramidi" oluşturur (örn. "Topluluğun %72'si Zidane'ı top 10'da görüyor").
- Bu içerik, **organik paylaşım ve sosyal medya** için güçlü bir kaynaktır.

**Bu mod yarışma değildir:** Chip/Rating yok; ancak **XP** (içerik üretimi ödülü) ve **beğeni/etkileşim** üzerinden hafif ödüllendirme verilebilir.

---

### 3.8. Baş Harflerden Futbolcu — "Harf Düellosu"
> *Şemadaki: soyadı baş ve son harfi verilir.*

**Tanım:** Soyadı belirli bir **harfle başlayıp** belirli bir **harfle biten** bir futbolcuyu ilk söyleyen kazanır.

**Online:**
1. Her iki kullanıcıdan **1'er harf** alınır (biri başlangıç, biri bitiş).
2. Soyadı 1. harf ile başlayıp 2. harf ile biten ilk geçerli futbolcuyu söyleyen kazanır.
3. **30 saniye** içinde cevap gelmezse kimse puan almaz (beraberlik).

**Tek Oyunculu:**
1. Sistem 2 harf verir.
2. Oyuncu süre içinde uygun futbolcuyu bulur.

**Kenar durumları:**
- Çözülebilirlik: harf çifti için en az 1 oyuncu olmalı. Online'da kullanıcılar harf seçtiği için **imkânsız çift** oluşabilir → *(Tasarım Kararı: sistem, harfler seçildikten sonra çözüm olup olmadığını kontrol eder; çözüm yoksa beraberlik/yeni tur. Veya kullanıcılar yalnızca "çözümü olan" harf havuzundan seçer.)*
- Soyadı vs tam ad: bazı oyuncular tek isimle bilinir (Ronaldinho). *(Tasarım Kararı: veritabanında "sıralama adı / soyadı" alanı esas alınır; her ikisi de kabul edilebilir.)*
- Transkripsiyon (İ/ı, ş, ç): Türkçe ve uluslararası karakter normalizasyonu gerekir.

---

### 3.9. Bayraklarla İlk 11'i Bul — "Bayrak XI"
> *Şemadaki: ilk 11'deki oyuncuların uyruk bayrakları mevkilere konur.*

**Tanım:** Bir takımın belirli bir maçtaki/dönemdeki ilk 11'i, oyuncuların **uyruk bayrakları** ile mevkilerine yerleştirilir. Oyuncu bu takımı (veya kadroyu) tahmin eder.

**Akış:**
1. Saha şeması + mevkilerde bayraklar gösterilir.
2. Oyuncu takımı tahmin eder. *(Tasarım Kararı: ya takım adı, ya da kademeli olarak oyuncu isimleri tahmini.)*

**Online:** İlk bilen kazanır, yine de **3 hak** vardır.
**Tek Oyunculu:** Oyuncu **3 hakta** bulmaya çalışır.

**Kenar durumları:**
- Aynı uyruktan birden çok oyuncu (örn. tüm 11'i aynı milletten) → ipucu zayıflar; bu kadrolar zorluk olarak işaretlenir.
- Hangi tarih/maç? Belirli bir ikonik kadro veya tarih seçilir (örn. "şampiyonluk finali XI").
- Çift uyruklu oyuncular → birincil uyruk veya temsil edilen milli takım.

---

### 3.10. Oyuncu–Takım Örgüsü — "Zincir Oyunu"
> *Şemadaki: sırayla oyuncu/takım söyleme, tekrar olmaz.*

**Tanım:** 2+ kişiyle oynanan zincir oyunu. Oyuncu → takım → oyuncu → takım şeklinde bağ kurularak ilerler; daha önce söylenen tekrarlanamaz.

**Akış:**
1. 1. oyuncu bir futbolcu söyler (örn. *Messi*).
2. 2. oyuncu, o futbolcunun oynadığı bir takım söyler (örn. *Barcelona*).
3. 3. oyuncu, o takımda oynamış (ve **daha önce söylenmemiş**) bir oyuncu söyler.
4. Böyle devam eder. **15 saniyede** söyleyemeyen veya geçersiz/tekrar söyleyen **elenir**.
5. **Son 1 oyuncu** kalana kadar sürer; o kazanır.

**Yalnızca online** (gerçek zamanlı çoklu oyuncu).

**Kenar durumları:**
- Geçerlilik doğrulaması: söylenen oyuncu gerçekten o takımda oynamış mı (veritabanı kontrolü).
- Tekrar kontrolü: oturum geçmişi tutulur.
- İtiraz mekanizması: sistem otoritedir (veritabanına göre); itiraz gerekmez.
- "Açık uç" riski: zincir bir noktada çözümsüz kalabilir → *(Tasarım Kararı: sistem her adımda en az 1 geçerli devam olduğunu bilir; çözümsüz noktada tur sıfırlanır/yeni başlangıç.)*

---

### 3.11. Mod Karşılaştırma Tablosu

| # | Mod | Online | Tek Oyunculu | Yarışma | Para Birimi | Oturum Süresi |
|---|-----|:---:|:---:|:---:|---|---|
| 3.1 | Kariyer İstatistiği Avı | ✅ | ✅ | ✅ | Chip/XP | 60–120 sn |
| 3.2 | Sınırlı XI Kadro | ✅ | ✅ | ✅ | Chip/XP | 90–150 sn |
| 3.3 | Futbol Tic-Tac-Toe | ✅ | ✅ | ✅ | Chip/XP | 90–180 sn |
| 3.4 | İlk 10 Listesi | ✅ | ✅ | ✅ | Chip/XP | 60–120 sn |
| 3.5 | Kesişim Düellosu | ✅ | ❌ | ✅ | Chip/XP | 20–60 sn |
| 3.6 | Kariyer İzi | ✅ | ✅ | ✅ | Chip/XP | 30–90 sn |
| 3.7 | Sıralama Piramidi | ✅(sosyal) | ✅ | ❌ | XP/etkileşim | 30–60 sn |
| 3.8 | Harf Düellosu | ✅ | ✅ | ✅ | Chip/XP | 30 sn |
| 3.9 | Bayrak XI | ✅ | ✅ | ✅ | Chip/XP | 30–90 sn |
| 3.10 | Zincir Oyunu | ✅ | ❌ | ✅ | Chip/XP | 3–10 dk |
| 3.11 | — | — | — | — | — | — |

---

## 4. Ekonomi Sistemi

### 4.1. Genel Felsefe
İki para birimi, klasik ve kanıtlanmış F2P yapısını izler:
- **Gems = premium (hard) para** → nadir, satın alınabilir, "konfor/hız/statü".
- **Chip = yumuşak (soft) para** → bol, oyunla kazanılır, "bahis/oyun yakıtı".

**Altın kural:** Para harcayan oyuncu **zaman ve konfor** satın alır, **bilgi/yetenek** değil. Bu pay-to-win'i önler.

### 4.2. Gems (Mücevher)

**Kazanım yolları:**
| Kaynak | Açıklama |
|--------|----------|
| 4.2.1 IAP | Marketten gerçek para ile satın alma |
| 4.2.2 Lig 1.liği | Hafta/sezon sonunda kendi liginde 1. olana ödül |
| 4.2.3 Streak ödülü | 7 ve katları günlük oyun serisinde ödül |
| 4.2.4 Başlangıç | Her oyuncu **20 Gems** ile başlar |

**Harcama yolları (Gems Sink — KRİTİK, şemada eksik):**
> Bir ekonomi yalnızca kaynaklarla yaşamaz; **harcama noktaları (sink)** olmadan enflasyon olur. Gems için sink'ler:
- Chip satın alma (§4.3.2).
- 2× XP / 2× Chip süreli takviyeler (§4.3.3, §5.2).
- Avatar parçaları (premium kozmetikler).
- *(Önerilen ek sink'ler):* "yeniden eşleştirme/rakip atlama", "ekstra tahmin hakkı (tek oyunculu)", "ipucu satın alma", "lig koruma kalkanı", "isim değiştirme".

### 4.3. Chip

**Kazanım yolları:**
| Kaynak | Açıklama |
|--------|----------|
| 4.3.1 Oda kazançları | Odaya giriş ücreti ödenir; kazanan ödül havuzunun **%90'ını** alır (%10 rake) |
| 4.3.2 Gems takası | Gems ile marketten Chip alınır |
| 4.3.3 2× takviye | Gems ile oyun sonu Chip kazancına süreli 2× |
| 4.3.4 Başlangıç | Her oyuncu **1000 Chip** ile başlar |

**Harcama yolları (Chip Sink):**
- Oda giriş ücretleri (ana sink; rake ile döngüden Chip çeker → enflasyon kontrolü).
- Bazı avatar parçaları (Chip ile alınabilen ucuz kozmetikler).

### 4.4. Oda Sistemi (Tablerooms)
Her oyun modunun farklı giriş ücretli odaları vardır:

| Oda Seviyesi | Giriş Ücreti (örnek) | Hedef Kitle |
|--------------|----------------------|-------------|
| Acemi | 50 Chip | Yeni oyuncular, düşük risk |
| Standart | 250 Chip | Ortalama |
| Yüksek | 1.000 Chip | Tecrübeli |
| VIP/Elit | 5.000+ Chip | Yüksek statü |

**Ödül havuzu mekaniği (2 kişilik düello örneği):**
- Her oyuncu 250 Chip öder → havuz 500.
- Kazanan: 500 × 0,90 = **450 Chip** (net kâr +200).
- Rake: 50 Chip sistemce yakılır.

> **Rake'in rolü:** Sürekli Chip yakarak ekonomiyi dengeler; aksi halde toplam Chip arzı sınırsız büyür. %10 standart ve sürdürülebilir bir orandır.

### 4.5. Ekonomi Akış Diyagramı
```
GERÇEK PARA ──IAP──► GEMS ──┬──► Chip satın al ──► Chip
                            ├──► 2× takviyeler (XP/Chip)
                            └──► Premium avatar

OYUN (oda) ──kazan──► Chip ──► daha yüksek odalar (giriş ücreti)
   │                                    │
   └──── %10 rake (yakılır) ◄───────────┘   [enflasyon kontrolü]

GÜNLÜK STREAK / LİG 1.LİĞİ ──► GEMS  [ücretsiz premium kaynak → F2P adaleti]
```

### 4.6. Başlangıç Dengesi (İlk Oturum Matematiği)
- 20 Gems + 1000 Chip ile başlayan oyuncu: standart odada (250 Chip) ~4 maç oynayabilir; kaybetse bile birkaç tur deneyim kazanır.
- *(Tasarım Kararı: "iflas koruması" — Chip'i belirli eşiğin altına düşen oyunculara günlük küçük bir "acemi odası" bonusu/ücretsiz oda hakkı verilir; oyuncu ekonomiden tamamen düşmesin.)*

---

## 5. İlerleme Sistemi (Level / XP)

### 5.1. XP Kazanımı
- Her **online ve tek oyunculu** oyundan XP kazanılır.
- **Online:** Kazanınca **daha çok**, kaybedince **daha az** XP (kaybedene de bir miktar verilir → öğrenme/tutundurma).
- **Tek Oyunculu:** Oyun içi **performansa** göre hesaplanır:
  - Bitirme süresi (hızlı → çok)
  - Erken/verimli tahmin (az hata, az futbolcu)
  - Tamamlama oranı

**Örnek XP formülü (Tasarım Kararı — ayarlanabilir):**
```
Online kazanan  = TabanXP + (PerformansBonusu) + (RakipZorluğu * k)
Online kaybeden = TabanXP * 0.3
Tek Oyunculu   = TabanXP * (DoğrulukOranı) * (HızÇarpanı)
```

### 5.2. 2× XP Takviyesi
- Gems karşılığında, oyun sonu kazanılan XP'ye **süreli 2×** takviye alınabilir (örn. "30 dk boyunca tüm maçlar 2× XP").

### 5.3. Level Eğrisi
- *(Tasarım Kararı:* artan maliyetli eğri — her level bir öncekinden biraz daha fazla XP ister. Erken leveller hızlı (dopamin), ileri leveller yavaş (uzun vade).*)*
- Örnek: `gerekli_XP(level) = 100 * level^1.5`

### 5.4. Level Ödülleri
- Her **10/15 levelde** basit bir **avatar öğesi** kazanılır (§7.2).
- Ara levellerde küçük Chip/Gems ödülleri verilebilir (motivasyon).

### 5.5. Level vs Rank Ayrımı (Önemli)
- **Level:** Birikimli emek/zaman göstergesi (asla düşmez). "Ne kadar oynadım."
- **Rank/Elo:** Anlık beceri göstergesi (düşebilir). "Ne kadar iyiyim."
- İkisi ayrı tutulur; karıştırılmamalıdır.

### 5.6. Başarımlar (Achievements)
Oyuncuya uzun vadeli hedefler ve koleksiyon hissi veren rozet sistemi. Profilde sergilenir, sosyal teşhir + tutundurma sağlar.

**Kategoriler:**
| Kategori | Örnek Başarımlar |
|----------|------------------|
| İlerleme | "İlk galibiyet", "Level 10/25/50'ye ulaş", "100 maç oyna" |
| Beceri | "İlk 10'da tam liste (hatasız)", "5 maçlık galibiyet serisi", "Tic-Tac-Toe'da 3'lü diziyi 5 hamlede tamamla" |
| Mod ustalığı | Her mod için ayrı: "Kariyer İzi'nde 50 galibiyet" vb. |
| Rekabet | "Altın lige terfi et", "Bir hafta lig 1.si ol", "Efsane ligine ulaş" |
| Sadakat | "7/30/100 günlük streak", "Bir sezonu tamamla" |
| Sosyal | "5 arkadaş ekle", "Bir piramit yayınla ve 100 beğeni al" |

**Ödüller:** Her başarım, zorluğuna göre **XP + Chip/Gems + özel rozet/avatar parçası** verir.

**Katmanlar (Tasarım Kararı):** Bronz / Gümüş / Altın / Platin kademeli başarımlar (örn. "10 → 50 → 250 → 1000 maç") uzun vadeli hedef sağlar.

**Görünürlük:** Profilde vitrin (öne çıkarılan 3 rozet), tam başarım listesi ve ilerleme yüzdesi.

---

## 6. Rekabet Sistemi (Rank / Elo / Ligler)

### 6.1. Rating (Elo)
- Her **online** oyun sonunda: kazanan **rating kazanır**, kaybeden **kaybeder**.
- Her oyuncu **100 rating** ile başlar.
- *(Tasarım Kararı: standart Elo benzeri formül — beklenmedik galibiyet daha çok rating; favori galibiyeti az rating.)*
```
ΔR = K * (Sonuç − BeklenenSonuç)
BeklenenSonuç = 1 / (1 + 10^((R_rakip − R_oyuncu)/400))
K = 32 (yeni oyuncularda daha yüksek, oturdukça düşürülebilir)
```

### 6.2. Lig Yapısı
- Birden çok **lig (tier)** vardır; oyuncular bir tier içindeki gruplarda yarışır.
- Ligler haftalık **sıfırlanmaz**; oyuncular terfi/düşme ile ligler arasında hareket eder (bkz. §6.3).
- *(Tasarım Kararı: tier sistemi — örnek)*

| Lig | Açıklama | Renk/İkon |
|-----|----------|-----------|
| Bronz | Başlangıç ligi | 🥉 |
| Gümüş | — | 🥈 |
| Altın | — | 🥇 |
| Platin | — | 💎 |
| Elmas | — | 🔷 |
| Efsane | En üst lig | 👑 |

> **Not:** Oyuncular kendi liglerinde, hafta boyunca topladıkları rating/puana göre **grup içi sıralanır**. Lig değişimi rating eşiğiyle değil, **haftalık sıralamadaki konumla** (terfi/düşme barajı) belirlenir.

### 6.3. Haftalık Lig Döngüsü
1. Hafta boyunca oyuncular oynar ve lig içi puan/rating toplar.
2. Hafta sonu: oyuncular kendi ligindeki sıralamaya göre dizilir.
3. **1. olan oyuncuya Gems ödülü** (§4.2.2).
4. **Terfi-düşme-kalma uygulanır:**
   - **İlk %10** bir üst lige **terfi** eder.
   - **Son %10** bir alt lige **düşer**.
   - **Geri kalan %80** aynı ligde **kalır**.
   *(Yüzdeler ayarlanabilir; bu varsayılan dengedir.)*
5. Yeni hafta başlar; oyuncu yeni lig grubunda devam eder.

> **Kenar durumları:**
> - En üst lig (Efsane) oyuncuları terfi edemez; sadece kalır veya düşer.
> - En alt lig (Bronz) oyuncuları düşemez; sadece kalır veya terfi eder.
> - Yüzde hesabı her lig grubunun oyuncu sayısına göre yapılır; çok küçük gruplarda en az 1 terfi / 1 düşme garanti edilebilir.

### 6.4. Sezon
- Birden çok haftadan oluşan "sezon" katmanı (örn. 8 hafta).
- **Sezon sonu** büyük ödüller (Gems, özel avatar, rozet).
- Yeni sezonda yumuşak rating sıfırlama (soft reset) — herkese taze başlangıç ama tecrübe korunur.

### 6.5. Lider Tabloları (Leaderboards)
Haftalık lig sıralamasının yanında, daha geniş kapsamlı sıralama ekranları bulunur.

| Lider Tablosu | Kapsam | Sıralama Ölçütü |
|---------------|--------|------------------|
| **Global** | Tüm oyuncular | Rating (ve/veya sezon puanı) |
| **Bölgesel/Ülke** | Aynı ülke oyuncuları | Rating |
| **Arkadaşlar** | Kullanıcının arkadaş listesi | Rating |
| **Mod bazlı** | Tek bir oyun modu | O moda özel puan/galibiyet |
| **Haftalık lig** | Oyuncunun mevcut lig grubu | Haftalık puan (§6.3) |

**Arkadaş Sıralaması (özellikle istenen):** Sıralamalar ekranında, kullanıcı kendini yalnızca **arkadaşları arasında** görebileceği bir sekme bulur. Bu, geniş global tabloda kaybolmadan yakın çevreyle rekabeti teşvik eder ve güçlü bir tutundurma kancasıdır.

**Tasarım notları:**
- Her tabloda kullanıcının kendi sırası her zaman görünür (listenin çok altında olsa bile "sen buradasın" satırı).
- Global tablo çok büyük olacağından sayfalama + "yakınımdakiler" görünümü.
- Anti-cheat ile temizlenmiş veriler gösterilir (şüpheli hesaplar gizlenir).

---

## 7. Avatar ve Özelleştirme

### 7.1. Sistem
- Her kullanıcının bir **avatarı** vardır.
- Marketten **Gems/Chip** karşılığı parçalarla özelleştirilir:
  - Forma, atkı, krampon, şapka, vb. (genişletilebilir slotlar: saç, yüz, arka plan, çerçeve, rozet).

### 7.2. Edinim Yolları
| Yol | Para Birimi |
|-----|-------------|
| Market satın alma | Gems (premium parçalar) / Chip (temel parçalar) |
| Level ödülü | Her 10/15 levelde 1 basit parça (ücretsiz) |
| Sezon/lig ödülü | Özel/nadir parçalar (statü) |
| Streak/etkinlik | Sınırlı süreli özel parçalar |

### 7.3. Nadirlik Katmanları (Tasarım Kararı)
- **Yaygın** (Chip) → **Nadir** (Gems) → **Efsanevi** (yalnızca lig/sezon ödülü, satın alınamaz).
- Satın alınamayan statü parçaları, rekabetçi oyuncular için güçlü bir motivasyon kaynağıdır.

### 7.4. Görünürlük
- Avatar, lig tablolarında, eşleşme ekranında ve profil sayfasında görünür → **sosyal teşhir = motivasyon**.

---

## 8. Online Altyapı

### 8.1. Eşleştirme (Matchmaking) — *Şemada eksik, zorunlu*
- **Hızlı eşleştirme:** Seçilen oda ücreti + benzer rating aralığındaki oyuncularla eşleştirme.
- **Arkadaşla oyna:** Davet kodu / link ile özel oda.
- **Bot yok:** Eşleştirmede bot kullanılmaz. Rakip bulunamazsa oyuncu bekleme ekranında tutulur, dilerse iptal edip **tek oyunculu modlara** yönlendirilir. Tüm online maçlar gerçek oyunculararasıdır.

### 8.2. Gerçek Zamanlı Senkronizasyon
- Düşük gecikme gerektiren modlar (Kesişim Düellosu, Harf Düellosu, Zincir): WebSocket tabanlı kalıcı bağlantı.
- **Sunucu otoritesi:** Tüm doğrulama (cevap geçerliliği, zamanlayıcı, kim önce bildi) sunucuda yapılır; istemciye güvenilmez.

### 8.3. Hile Önleme (Anti-Cheat) — *Şemada eksik, KRİTİK*
Bilgi yarışmasında en büyük tehdit: oyuncunun başka cihazdan/internetten arama yapması.
- **Sunucu doğrulaması:** Tüm cevaplar sunucuda doğrulanır.
- **Süre baskısı:** Kısa zamanlayıcılar (harici arama için vakit bırakmaz) → tasarımın doğal hile önleyicisi.
- **Anomali tespiti:** Anormal yüksek doğruluk + yavaş cevap süresi (arama imzası) işaretlenir.
- **Eşleştirme bütünlüğü:** Aynı IP/cihazdan iki hesabın "Chip transferi" için eşleşmesini (collusion) önleme.
- **Sunucu otoriter zamanlayıcı:** İstemci saat manipülasyonu engellenir.
- **Rapor/ban sistemi:** Şüpheli hesaplar için.

### 8.4. Adillik
- Eşleştirme rating tabanlı → güçlü oyuncu yeni başlayanı ezmez.
- Soğuk başlangıç (yeni oyuncu) için kademeli zorluk artışı.

> **Not:** Tek oyunculu modlar da sunucuya bağlıdır. Bilgi/soru verisi cihazda tutulmaz; bu hem içerik güvenliği (kopyalanamaz) hem hile önleme hem de güncellenebilirlik için zorunludur.

### 8.5. Hesap ve Giriş Sistemi
Tüm kullanıcılar **kayıtlıdır**; misafir/anonim oyun yoktur (ekonomi ve rekabet bütünlüğü için).

**Desteklenen giriş yöntemleri:**
- **Google Play Games / Google ile giriş** (Android)
- **Apple ile giriş** (iOS — App Store politikası gereği üçüncü taraf giriş varsa Apple girişi de zorunludur)
- **E-posta + şifre** (platform bağımsız)

**Gereksinimler:**
- **Cihazlar arası senkron:** Hesap bulutta tutulur; oyuncu farklı cihazda giriş yaptığında tüm ilerleme (Level, Rating, Gems, Chip, avatar, başarımlar) eş zamanlı gelir.
- **Hesap birleştirme:** Aynı kişi birden çok yöntemle giriş yaptıysa hesapları tek kimliğe bağlama.
- **Hesap kurtarma:** E-posta doğrulama ile şifre sıfırlama.
- **Tek otoriter kaynak:** Tüm bakiye ve ilerleme sunucuda saklanır (§13.5); istemci yalnızca gösterir → cihaz değişiminde veri kaybı/hilesi olmaz.
- **Oturum güvenliği:** Token tabanlı kimlik doğrulama; aynı hesabın aynı anda birden fazla aktif online oturumu engellenir.

### 8.6. Sosyal Sistem (Sınırlı Kapsam)
*(Tasarım Kararı: Bilinçli olarak hafif tutuldu — klan, grup sohbeti vb. yok. Yalnızca:)*
- **Arkadaş ekleme:** Kullanıcı adı/etiket veya davet linkiyle arkadaş ekleme; istek gönder/kabul et.
- **Özel oda kurma:** Arkadaşlarla davet kodu/link üzerinden, ücretli veya ücretsiz özel maç odaları (§8.1).
- **Arkadaş sıralaması:** Sıralamalar ekranında arkadaşlar arası lider tablosu (§6.5).
- **Profil görüntüleme:** Arkadaşın avatarı, level, rozetleri ve istatistikleri.

> **Kapsam dışı (şimdilik):** Klanlar/takımlar, serbest sohbet (chat), forum. Bu, hem moderasyon yükünü hem de geliştirme kapsamını düşük tutar.

### 8.7. Kullanıcı Üretimi İçerik (UGC) Moderasyonu
Açık metin içeren alanlar moderasyon gerektirir:
- **Kullanıcı adları:** Kayıt sırasında küfür/uygunsuz/taklit (impersonation) filtresi (kara liste + desen kontrolü).
- **Piramit yayınları (§3.7):** Yalnızca veritabanındaki oyuncu/takım seçilebildiği için serbest metin riski düşüktür; yine de yayın akışı için **raporlama** butonu bulunur.
- **Raporlama & yaptırım:** Kullanıcılar uygunsuz isim/davranış raporlayabilir; tekrarlayan ihlallerde uyarı → geçici askı → kalıcı ban.
- **Otomatik + manuel:** İlk savunma otomatik filtre; sınırda kalan vakalar manuel inceleme kuyruğuna düşer.

---

## 9. Veri Modeli ve İçerik Kaynağı

> Bu oyunun kalbi **veridir**. Yanlış/eksik veri = bozuk oyun. Bu bölüm ürünün en kritik teknik bağımlılığıdır.

### 9.1. Gereken Veri Varlıkları
| Varlık | Alanlar (örnek) |
|--------|------------------|
| Futbolcu | ad, sıralama_adı, uyruk(lar), doğum_tarihi, boy, mevki(ler), güncel_kulüp |
| Kariyer kaydı | futbolcu_id, kulüp_id, başlangıç_yılı, bitiş_yılı, kiralık_mı, maç, gol, asist, sarı, kırmızı |
| Kulüp | ad, kısaltma, ülke, lig_id, logo |
| Lig | ad, ülke, seviye |
| İlk 11 / kadro | takım_id, maç/dönem, mevki→futbolcu eşlemesi |

### 9.2. Veri Kaynağı Seçenekleri (Tasarım Kararı)
1. **Ücretli API** (örn. profesyonel futbol veri sağlayıcıları) — güncel, lisanslı, maliyetli.
2. **Açık veri + manuel doğrulama** — düşük maliyet, yüksek bakım yükü, lisans riski.
3. **Hibrit** — temel veri lisanslı API'den, "tüm zamanlar/tarihî" veri için ek kaynak.

> **Lisans/telif uyarısı:** Oyuncu isimleri, kulüp adları, logoları ve veri kullanımı lisans gerektirebilir. Hukuki danışmanlık alınmalı. Logolar yerine jenerik temsiller, isimler için "gerçek kişi verisi" lisansı netleştirilmeli.

### 9.3. Veri Güncelliği
- "Aktif oyuncu" ve "güncel kulüp" gibi alanlar transfer dönemlerinde değişir → **otomatik güncelleme pipeline'ı** gerekir.
- Modlar veri tarihine bağlı (§3.2, §3.4): "güncellik tarihi" UI'da gösterilebilir.

### 9.4. Çözülebilirlik Motoru (Solvability Engine)
Birçok mod (Tic-Tac-Toe, Kesişim, Harf, Zincir) **çözümü olan** bulmaca üretmek zorundadır:
- Sistem önce veritabanından **geçerli çözümleri** bulur, sonra bulmacayı kurar.
- Üretilen her bulmaca için "en az 1 cevap var" garantisi test edilir.
- **Zorluk derecelendirme:** Çözüm sayısı az olan bulmacalar "zor", çok olanlar "kolay" işaretlenir → zorluk ayarı.

### 9.5. İsim Eşleştirme / Autocomplete
- Tüm metin girişli modlarda **autocomplete** zorunlu (imla hatalarını, eşadlılığı, transkripsiyon farklarını çözer).
- Türkçe/uluslararası karakter normalizasyonu (İ/ı, ş, ö, ç, aksanlar).
- Lakap eşlemesi (Pelé, Ronaldinho, Kaká).

---

## 10. Kullanıcı Arayüzü, Sanat Yönetimi, Ses ve Erişilebilirlik

### 10.1. Ana Ekranlar
| Ekran | İçerik |
|-------|--------|
| Ana Menü (Home) | Mod seçimi, günlük ödül, streak, hızlı oyna |
| Mod Seçim | 11 mod kartı, online/tek oyunculu anahtarı |
| Oda Seçim | Giriş ücreti seviyeleri, ödül havuzu önizleme |
| Eşleştirme | Rakip aranıyor / rakip bulundu animasyonu |
| Oyun Ekranı | Moda özel (her mod için ayrı tasarım) |
| Sonuç Ekranı | Kazanç (Chip/XP/Rating), level/rank ilerlemesi, "tekrar oyna" |
| Lig Tablosu | Haftalık sıralama, lig tier'ı, terfi/düşme barajı |
| Market | Gems/Chip paketleri, avatar parçaları, takviyeler |
| Avatar/Profil | Özelleştirme, istatistikler, rozetler |
| Sosyal | Arkadaşlar, davet, piramit akışı (§3.7) |

### 10.2. İlk Açılış Akışı (First Launch)
```
Splash → Hesap girişi/kayıt (Google / Apple / E-posta — zorunlu)
   → Hoşgeldin & başlangıç bonusu (20 Gems, 1000 Chip)
   → Kısa etkileşimli eğitim (1 kolay tek oyunculu mod) → Ana Menü
```

### 10.3. UI İlkeleri
- Her tek el **hızlı erişim** (en fazla 2 dokunuşta oyuna girme).
- Sonuç ekranında **net ödül geri bildirimi** (animasyonlu Chip/XP akışı = dopamin).
- Zamanlayıcı her zaman görünür ve adil (sunucu senkronu).

### 10.4. Sanat Yönetimi ve Görsel Kimlik
*(Henüz tasarım aşamasına geçilmedi; bu bölüm sağlam bir çerçeve sunar, üretim öncesi netleştirilecek.)*

**Genel yön (öneri):** Modern, enerjik, "spor uygulaması + bilgi yarışması" hissi. Stadyum/saha çağrışımları (çim yeşili dokular, saha çizgileri) ile temiz, okunaklı arayüz dengesi.

**Tasarım sistemi (Design System) gereksinimleri:**
- **Renk paleti:** Birincil (marka), ikincil (vurgu/CTA), nötr (arka plan/metin) ve **anlamsal renkler** (başarı/yeşil, hata/kırmızı, uyarı/sarı). Tüm renkler erişilebilir kontrast oranlarını sağlamalı (§10.6).
- **Tipografi:** Başlık + gövde için en fazla 2 yazı tipi; rakamlar için net, hızlı okunan bir tip (skor/süre çok kullanılır).
- **İkonografi:** Tutarlı ikon seti; mevkiler, para birimleri (Gems/Chip), modlar için ayırt edici simgeler.
- **Bileşen kütüphanesi:** Buton, kart, modal, sayaç, ilerleme çubuğu, lider tablosu satırı, oyuncu/takım rozeti — yeniden kullanılabilir.
- **Avatar sistemi:** Katmanlı (forma, atkı, krampon, şapka, arka plan, çerçeve) ve genişletilebilir.
- **Animasyon dili:** Ödül akışı, doğru/yanlış geri bildirimi, terfi/düşme kutlaması, sayaç baskısı için tutarlı micro-interaction'lar.

**Tonal kimlik:** Rekabetçi ama eğlenceli; agresif değil. Futbol kültürüne saygılı, evrensel (belirli kulüp taraftarlığına yaslanmadan).

**Üretim notu:** Lisans nedeniyle (§9.2, §16) gerçek kulüp logoları/oyuncu fotoğrafları yerine jenerik temsiller (silüet, baş harf rozetleri, jenerik bayraklar) varsayılan olarak tasarlanmalı; lisans alınırsa zenginleştirilir.

### 10.5. Ses ve Müzik (Audio Design)
*(Başlangıçta düşünülmemişti; tutundurma ve his için önemli, bu nedenle çerçeve ekleniyor. Önceliği MVP sonrası olabilir.)*

| Katman | İçerik |
|--------|--------|
| **Müzik** | Hafif, tekrar dinlenebilir menü müziği; maç sırasında düşük yoğunluklu/gerilim müziği (özellikle süre azalırken) |
| **SFX (ses efektleri)** | Doğru cevap, yanlış cevap, süre tik-takı, ödül kazanma, level atlama, terfi/düşme, buton dokunuşu |
| **Haptik (titreşim)** | Doğru/yanlış geri bildirimi, süre kritik eşiği, kazanma anı (mobilde his güçlendirir) |
| **Ses ipuçları** | Süre bitmek üzereyken artan tempo/uyarı sesi |

**İlkeler:**
- **Tam kontrol:** Müzik ve SFX ayrı ayrı açılıp kapatılabilir (ayarlar).
- **Sessiz oynanabilirlik:** Oyun sessizde tam oynanabilir olmalı (toplu taşıma vb.); ses asla zorunlu bilgi taşımaz (erişilebilirlik).
- **Yorucu olmama:** Kısa, tekrar eden oturumlar için ses tasarımı rahatsız edici/aşındırıcı olmamalı.

### 10.6. Erişilebilirlik (Accessibility)
**Renk körlüğü (özellikle önemli):** Oyunda kırmızı/yeşil ayrımına dayanan iki kritik nokta var — **Piramit (§3.7)** ve **Tic-Tac-Toe (§3.3)** + anlamsal doğru/yanlış renkleri. En yaygın renk körlüğü tam da kırmızı-yeşil olduğundan, ayrım **asla yalnızca renge** dayandırılmaz:
- **Çift kodlama:** Renk + **ikon/şekil** birlikte. Örn:
  - Piramit: yeşil katman ✓ (onay ikonu) + dolu desen; kırmızı katman ✗ (çarpı ikonu) + çizgili/farklı desen.
  - Tic-Tac-Toe: oyuncular renkle değil aynı zamanda **sembolle** (örn. ● vs ▲ veya X vs O) ayrılır.
  - Doğru/yanlış: ✓/✗ ikonları + renk.
- **Renk körü dostu palet:** Anlamsal renkler, yaygın renk körlüğü türlerinde ayırt edilebilen tonlardan seçilir (örn. mavi-turuncu kombinasyonu güvenlidir).
- **Renk körü modu (opsiyonel):** Ayarlarda alternatif palet seçeneği.

**Diğer erişilebilirlik önlemleri:**
- **Metin/kontrast:** WCAG AA kontrast oranları; ölçeklenebilir yazı boyutu.
- **Dokunma hedefleri:** Minimum ~44×44 pt dokunma alanı.
- **Süre esnekliği:** Tek oyunculu modlarda daha uzun/kapatılabilir süre seçeneği (online'da adalet için sabit).
- **Ses bağımsızlığı:** Tüm kritik bilgi görsel olarak da verilir (§10.5).

---

## 11. Onboarding, Tutorial ve Tutundurma (Retention)

### 11.1. Onboarding
- İlk oturumda **kolay bir tek oyunculu mod** ile başlat (Bayrak XI veya İlk 10) → erken başarı hissi.
- Başlangıç bonusu (20 Gems, 1000 Chip) anında kullanılabilir.
- Kademeli mod tanıtımı (hepsini birden değil).

### 11.2. Mod Başına Tutorial
11 modun her biri farklı kural ve arayüze sahip olduğu için, **her mod kendi tutorial'ına** sahiptir.

**İlkeler:**
- **İlk girişte tetiklenir:** Oyuncu bir modu ilk kez açtığında o moda özel kısa, etkileşimli eğitim çalışır (anlatım değil, "yaparak öğren").
- **Atlanabilir & tekrar edilebilir:** Tutorial atlanabilir; mod ekranındaki "?" / "Nasıl oynanır" butonuyla istendiğinde tekrar açılır.
- **Kısa ve bağlamsal:** Adım adım ipucu balonları (örn. "Buraya iki takımda da oynamış bir futbolcu yaz").
- **Ücretsiz/risksiz ilk el:** İlk deneme tek oyunculu ve Chip riski olmadan yapılır; oyuncu mekaniği güvenle öğrenir.
- **Mod kartında durum:** Henüz oynanmamış modlar "Yeni" rozetiyle işaretlenir.

**Her tutorial şunları öğretir:** modun amacı, kazanma koşulu, giriş/etkileşim yöntemi (yazma/seçme), hak/süre kuralları, puanlama.

### 11.3. Günlük Tutundurma (Retention Hooks)
| Mekanik | Açıklama |
|---------|----------|
| Günlük streak | 7 ve katlarında Gems ödülü (§4.2.3) |
| Günlük görev | "Bugün 3 maç kazan", "2 farklı mod oyna" → Chip/XP |
| Haftalık lig | Hafta sonu sıralama baskısı → geri dönüş |
| Başarımlar | Uzun vadeli hedefler (§5.6) |
| Süreli etkinlikler | "Bu hafta sadece İtalyan ligi" temalı turnuvalar |

### 11.4. Sosyal Tutundurma
- Piramit paylaşımı (§3.7) → organik viral döngü.
- Arkadaş davet ödülü.
- Arkadaş sıralamasında rekabet (§6.5).

### 11.5. Geri Kazanım (Re-engagement)
- Push bildirim: "Liginde 2. sıraya düştün!", "Streak'in bozulmak üzere", "Arkadaşın seni düelloya çağırdı".

---

## 12. Monetizasyon

### 12.1. Gelir Kaynakları
1. **IAP (birincil):** Gems paketleri (örn. küçük/orta/büyük/değerli + ilk alım bonusu).
2. **Chip paketleri:** Doğrudan Chip satın alma (Gems üzerinden veya direkt).
3. **Takviyeler:** 2× XP / 2× Chip süreli boost'lar.
4. **Premium avatar:** Kozmetik (pay-to-win değil).
5. *(Faz 2 — opsiyonel):* Ödüllü reklam (tek oyunculu oyun sonunda "1 reklam izle, kazancını 2×"), "battle pass / sezon geçişi" (sezonluk ödül yolu).

### 12.2. Battle Pass / Sezon Geçişi (Önerilen, şemada yok)
- Sezon boyunca XP ile dolan iki paralel ödül yolu: **ücretsiz** ve **premium (Gems/IAP)**.
- Kanıtlanmış, adil ve yüksek getirili F2P monetizasyon; mevcut sezon yapısıyla (§6.4) doğal uyum.

### 12.3. Monetizasyon İlkesi
- **Pay-to-win yasak.** Para yalnızca: hız (boost), konfor (ekstra hak/ipucu), statü (kozmetik) satın alır.
- Doğru cevap her zaman bilgi gerektirir; satın alınamaz.

---

## 13. Teknik Mimari

### 13.1. İstemci
- **Tasarım Kararı:** Çapraz platform için **Flutter** (UI ağırlıklı, animasyonlu) veya **Unity** (oyunsu his/animasyon yoğunsa). 11 mod çoğunlukla UI/form tabanlı → Flutter güçlü aday.

### 13.2. Sunucu
- **Gerçek zamanlı:** WebSocket sunucusu (düello/zincir modları için).
- **Oyun mantığı:** Sunucu otoriter (doğrulama, zamanlayıcı, eşleştirme, ekonomi işlemleri).
- **REST/GraphQL API:** Profil, market, lig, veri sorguları.

### 13.3. Veritabanları
- **Oyuncu/işlem verisi:** İlişkisel DB (ekonomi işlemleri için ACID — Chip/Gems tutarlılığı kritik).
- **Futbol bilgi verisi:** İlişkisel + indeksli arama (kesişim sorguları, autocomplete).
- **Önbellek:** Sık sorgulanan bulmacalar/listeler için cache (Redis vb.).
- **Lider tablosu/rating:** Hızlı sıralama için uygun yapı (sorted set vb.).

### 13.4. Backend Servisleri
- Eşleştirme servisi · Ekonomi servisi (atomik işlemler) · Rating/lig servisi · Bulmaca üretim & çözülebilirlik servisi · Veri güncelleme pipeline'ı · Anti-cheat/anomali servisi · Bildirim servisi · IAP doğrulama (Apple/Google makbuz kontrolü).

### 13.5. Ekonomi Bütünlüğü (Kritik)
- Tüm Chip/Gems hareketleri **sunucu tarafında**, **idempotent** ve **denetlenebilir (audit log)** olmalı.
- İstemci asla bakiye belirleyemez; yalnızca gösterir.
- IAP makbuzları her zaman sunucuda doğrulanır (sahte satın alma önleme).

---

## 14. KPI'lar ve Analitik

### 14.1. Tutundurma
- D1 / D7 / D30 retention.
- Streak süresi dağılımı.
- Günlük/haftalık aktif kullanıcı (DAU/WAU).

### 14.2. Etkileşim
- Oturum başına oynanan el sayısı.
- Mod popülerliği (hangi mod ne kadar oynanıyor).
- Online vs tek oyunculu oranı.

### 14.3. Ekonomi
- Toplam Chip arzı vs sink (enflasyon takibi).
- Gems kazanım/harcama oranı.
- Rake gelir (yakılan Chip).
- ARPU / ARPPU, dönüşüm oranı (ödeme yapan %).

### 14.4. Rekabet
- Rating dağılımı (sağlıklı çan eğrisi mi).
- Lig terfi/düşme oranları.
- Eşleştirme bekleme süresi.

### 14.5. Kalite
- Bulmaca itiraz/hata oranı (yanlış veri tespiti).
- Hile şüphesi işaretleme oranı.

---

## 15. Geliştirme Yol Haritası ve MVP Kapsamı

### 15.1. MVP (Faz 1) — "Çekirdek Eğlence Kanıtı"
Amaç: en az modla eğlence ve teknik altyapıyı doğrulamak.
- **Modlar (3 seçili):** Kariyer İzi (3.6), İlk 10 Listesi (3.4), Kesişim Düellosu (3.5) — biri tek oyunculu-ağırlıklı, biri liste, biri gerçek zamanlı düello → tüm teknik kasları test eder.
- **Sistemler:** Hesap & giriş (Google/Apple/E-posta) + cihazlar arası senkron, temel ekonomi (Chip + oda), XP/Level, basit online eşleştirme, autocomplete, çözülebilirlik motoru, veri pipeline temeli, **bu 3 mod için tutorial**, temel erişilebilirlik (renk körlüğü çift kodlama).
- **Yok:** Gems IAP (ya da minimal), avatar, gelişmiş lig, başarımlar, gelişmiş ses — sonraya.

### 15.2. Faz 2 — "Meta ve Monetizasyon"
- Gems + IAP, market, avatar/özelleştirme, takviyeler.
- Tam rank/lig/sezon sistemi + terfi/düşme.
- Global/arkadaş lider tabloları (§6.5), başarımlar (§5.6).
- Ses/müzik tasarımı (§10.5).
- 3–4 mod daha (Tic-Tac-Toe, Bayrak XI, Harf Düellosu, Kadro Kurma) + her biri için tutorial.

### 15.3. Faz 3 — "Sosyal ve Büyüme"
- Sıralama Piramidi + sosyal akış (3.7), Zincir Oyunu (3.10), İki Takım modu (3.5'in 2. türü dahil).
- Battle pass, etkinlikler, arkadaş sistemi + özel odalar, UGC moderasyon araçları.
- Kalan modlar.

### 15.4. Faz 4 — "Ölçek"
- Web platformu, yeni ligler/veri, dil yerelleştirme, turnuvalar.

---

## 16. Yasal Uyumluluk ve Regülasyon

> **Uyarı:** Bu bölüm genel bir çerçevedir, hukuki tavsiye değildir. Yayın öncesi mutlaka uzman hukuki danışmanlık alınmalıdır; kurallar ülkeye göre değişir.

### 16.1. Kumar / Şans Oyunu Riski ve Tasarımsal Önlem
Gerçek parayla satın alınan birim + "oda bahsi" kombinasyonu bazı ülkelerde kumar mevzuatına girebilir. **Bu oyunun kritik koruması:**
- **Chip gerçek paraya geri çevrilemez (cash-out yok).** Kazanılan Chip yalnızca oyun içinde harcanır; nakde, hediye kartına veya başka bir değere dönüştürülemez.
- Bu özellik, çoğu yargı bölgesinde "kumar" tanımının temel unsurlarından biri olan **gerçek para ödülü (real-world payout)** koşulunu ortadan kaldırır ve oyunu büyük olasılıkla bir **beceri temelli eğlence oyunu** kategorisinde tutar.
- Ek güçlendirici: Sonuç **şansa değil bilgiye/beceriye** dayanır (§ tasarım ilkesi 1).

**Yine de gözetilmesi gerekenler:**
- Chip transferinin oyuncular arası yapılamaması (kara para / dolaylı nakde çevirme önlemi).
- Bazı ülkelerin "para benzeri" sanal birimlere özel kuralları olabilir → ülke bazlı hukuki kontrol.

### 16.2. Loot Box / Şans Kutusu
- Mevcut tasarımda **rastgele içerikli ücretli kutu yoktur** (avatar parçaları doğrudan satılır). Bu, loot box regülasyonlarından (örn. bazı AB ülkeleri, belirli yaş derecelendirme kurulları) kaçınmayı sağlar.
- İleride rastgele ödül kutusu eklenirse: **olasılık açıklaması (drop rate disclosure)** zorunlu hale gelebilir; eklenmeden önce yeniden değerlendirilmeli.

### 16.3. Yaş Derecelendirmesi ve Reşit Olmayanlar
- App Store / Google Play yaş derecelendirmesi: IAP ve (varsa) sosyal etkileşim nedeniyle uygun kategori seçilmeli.
- **Reşit olmayan harcaması:** Ebeveyn kontrolü, platform satın alma onayları; mümkünse yaşa göre harcama sınırlandırması.
- Şans/bahis algısı yaratan içerik, düşük yaş derecelendirmesini riske atabilir → §16.1 önlemleri burada da koruyucu.

### 16.4. Veri Gizliliği (KVKK / GDPR)
- Kayıt zorunlu olduğundan (§8.5) kişisel veri işlenir (e-posta, platform kimliği, oyun verisi).
- **Gereklilikler:** Açık rıza, gizlilik politikası, veri işleme amacı şeffaflığı, **veri silme/taşıma hakkı** (hesap kapatma → veri silme), veri minimizasyonu.
- Çocuk verisi için ek koruma (KVKK ve GDPR-K/COPPA benzeri kurallar).
- Sunucu konumu ve veri aktarımı (yurt dışı aktarım) kurallarına uyum.

### 16.5. Platform ve Ticari Uyum
- **IAP zorunluluğu:** Dijital mal satışında Apple/Google'ın kendi ödeme sistemleri kullanılmalı (komisyon dahil).
- **Apple ile Giriş zorunluluğu:** Üçüncü taraf giriş (Google) sunuluyorsa, iOS'ta Apple ile Giriş de sunulmalı (§8.5 buna uygun).
- **Tüketici hakları:** İade politikası, abonelik (varsa battle pass) şeffaflığı.

### 16.6. Fikri Mülkiyet (özet — detay §9.2)
- Oyuncu isimleri, kulüp adları/logoları, bayrak kullanımı lisans gerektirebilir.
- Varsayılan: jenerik temsiller; lisans alınırsa zenginleştirme (bkz. §10.4, §9.2).

---

## 17. Riskler ve Önlemler

| Risk | Etki | Önlem |
|------|------|-------|
| **Yasal/kumar sınıflandırması** | Yüksek | Chip nakde çevrilemez (§16.1); beceri temelli; ülke bazlı hukuki kontrol |
| **Veri lisansı/telif** | Yüksek | Erken hukuki danışmanlık; lisanslı API; jenerik logolar (§16.6) |
| **Veri gizliliği (KVKK/GDPR)** | Yüksek | Rıza, gizlilik politikası, veri silme hakkı (§16.4) |
| **Yanlış/eski veri** | Yüksek | Otomatik pipeline + manuel doğrulama + oyuncu itiraz mekanizması |
| **Hile (harici arama)** | Yüksek | Kısa süreler, sunucu doğrulama, anomali tespiti |
| **Ekonomi enflasyonu** | Orta-Yüksek | Rake (%10), Gems sink'leri, sürekli izleme |
| **Pay-to-win algısı** | Orta | Para yalnızca konfor/kozmetik; bilgi satılamaz |
| **Çözümsüz bulmaca** | Orta | Çözülebilirlik motoru zorunlu |
| **UGC / uygunsuz içerik** | Orta | İsim filtresi, raporlama, yaptırım kademesi (§8.7) |
| **Soğuk başlangıç (az oyuncu → uzun eşleşme)** | Orta | Tek oyunculu modlara yönlendirme, bölge bazlı havuz, bekleme ekranı; **bot kullanılmaz** |
| **Yüksek başlangıç içerik maliyeti** | Orta | MVP'de dar veri kapsamı (örn. tek lig), kademeli genişleme |
| **Mod fazlalığı (kapsam patlaması)** | Orta | Aşamalı yayın; MVP'de 3 mod |

---

## 18. Açık Sorular ve Kararlar

### Karara bağlanan konular
1. **İlk 10 puanlaması (§3.4):** ✅ **Sıra numarası kadar puan.** 10. sırayı bilen 10, 9'u bilen 9... 1'i bilen 1 puan.
2. **Lig döngüsü (§6.3):** ✅ **Sıfırlama yok; haftalık terfi-düşme-kalma.** İlk %10 terfi, son %10 düşer, kalan %80 ligde kalır.
3. **Tic-Tac-Toe kazanma (§3.3):** ✅ **3'lü dizi tamamlayan kazanır.** Dizi oluşmazsa yeni matris gelir, oyun devam eder.
4. **Kadro kurma (§3.2):** ✅ **1-4-3-3 dizilimi; mevkiler Kaleci/Defans/Ortasaha/Forvet** olarak girilir.
6. **Bot kullanımı (§8.1):** ✅ **Bot olmayacak.** Tüm online maçlar gerçek oyunculararası.

### Devam eden / açık konular
5. **Veri kaynağı (§9.2):** 🔄 Çözüm üretimi devam ediyor (kullanıcı tarafından ele alınıyor). Sağlayıcı, bütçe ve lisans kapsamı netleşince §9.2 güncellenecek.
7. **İsim/marka:** ⏳ Henüz karar verilmedi. Çalışma adı belirlenecek.
8. **İlk hedef lig(ler) — MVP (§15.1):** 🔄 Veri kaynağıyla aynı durumda; çözümü üretiliyor (kullanıcı tarafından ele alınıyor). MVP'nin hangi lig(ler)in verisiyle çıkacağı, veri kaynağı netleşince belirlenecek.

---

## 19. Sözlük (Glossary)

| Terim | Anlam |
|-------|-------|
| **Gems** | Premium (hard) para birimi; nadir, IAP ile alınır |
| **Chip** | Yumuşak (soft) para birimi; oyunla kazanılır, oda bahisleri; **gerçek paraya çevrilemez** |
| **Rake** | Ödül havuzundan alınan sistem kesintisi (%10) |
| **Sink** | Bir para biriminin ekonomiden çekildiği harcama noktası |
| **Rating / Elo** | Beceriye dayalı sıralama puanı |
| **Tier / Lig** | Oyuncuların gruplandığı seviye; terfi/düşme ile değişir |
| **Streak** | Ardışık günlük oyun serisi |
| **Tek Oyunculu (Singleplayer)** | Rakipsiz, sunucuya bağlı mod; veri cihazda tutulmaz (eski adıyla "offline") |
| **Solvability Engine** | Çözümü olan bulmaca üreten/test eden sistem |
| **Matchmaking** | Online rakip eşleştirme sistemi |
| **Leaderboard** | Lider tablosu (global / bölgesel / arkadaş / mod bazlı) |
| **Achievement** | Başarım/rozet; uzun vadeli hedef |
| **UGC** | Kullanıcı üretimi içerik (kullanıcı adı, piramit yayını vb.) |
| **Core Loop** | Oyuncunun tekrar tekrar yaşadığı temel oynanış döngüsü |
| **F2P** | Free-to-play (ücretsiz oyna) |
| **IAP** | In-app purchase (uygulama içi satın alma) |
| **Cash-out** | Oyun içi birimi gerçek paraya çevirme (bu oyunda **yoktur**) |
| **Collusion** | İki hesabın gizli anlaşmayla ekonomi sömürmesi |

---

*Doküman sonu — v1.1. Geri bildirim ve §18'deki kararlar netleştikçe güncellenecektir.*
