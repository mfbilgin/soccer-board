# Piramit Sıralaması Modu — "Sıralama Görüşü"

Bu mod, bir rekabet veya bilgi yarışması değil, tamamen **fikir belirtme ve topluluk oylaması** amacıyla tasarlanmış eğlenceli bir sosyal moddur.

::: danger Henüz kodlanmadı — isim çakışmasına dikkat
Kodda `pyramid.py` / `PyramidScreen.js` adını taşıyan dosyalar **bu modu değil**, [Top 10 Tahmin](/guide/game-modes/top-10-guess) modunu uyguluyor (tarihsel bir isimlendirme hatası). Burada anlatılan "evet/hayır fikir belirtme piramidi" için backend'de route, frontend'de ekran veya veritabanında ilgili bir tablo yok. Aşağıdaki spec doğrudan uygulanabilir şekilde kesinleştirilmiştir.
:::

## Mantık ve Piramit Yapısı
Sistem kullanıcıya tartışmalı bir oyuncu veya takım sunar. Piramit aşağıdan yukarıya doğru şu sıralamalarla daralır: **İlk 50, İlk 25, İlk 10, İlk 5, İlk 3 ve 1. Sıra (Zirve).**

## Özne Seçimi (kesin algoritma)
Kullanıcıya rastgele bir özne dayatılmaz — kullanıcı önce **tür seçer** (Oyuncu / Takım), sonra arama kutusuyla ([TicTacToe](/guide/game-modes/tictactoe-4x4)'daki `/search` deseniyle aynı) istediği oyuncuyu/takımı kendisi bulup piramidini o özne için oluşturur. Bu, "tartışmalı/popüler özne" listesi tutma ihtiyacını ortadan kaldırır ve tasarımı basitleştirir.

## Oylama Akışı
- Piramit en alttan başlar: *"[Özne], tarihin en iyi 50'si arasında mıdır?"*
- Kullanıcı "Evet" derse katman **yeşil** olur, bir üst katman sorulur: *"İlk 25'te midir?"*
- Kullanıcı "Hayır" derse o katman **kırmızı** olur ve oylama **orada durur**; ilk "Hayır"dan sonraki tüm üst katmanlar otomatik olarak kırmızı kabul edilir (kullanıcıya ayrıca sorulmaz).
- *Örnek:* Zidane top 50 ✅ → top 25 ✅ → top 10 ❌ → üstü otomatik kırmızı, piramit 3 katman doldurulmuş ve tamamlanmış sayılır.
- Renk körlüğü erişilebilirliği için her katman renk + ikon (yeşil = ✓ ikonu, kırmızı = ✕ ikonu) ile çift kodlanır.

## Yayınlama (Publish) ve Sosyal Katman
1. Kullanıcı piramidini tamamladıktan sonra "Yayınla" butonuna basar; bu, `pyramid_rankings` tablosuna `published = true` olarak kaydedilir (aşağıya bkz.).
2. Yayınlanmayan piramitler yalnızca kullanıcının kendi profilinde taslak olarak durur, başkası göremez.
3. Yayınlanan piramitlere diğer oyuncular **Katılıyorum / Katılmıyorum** (agree/disagree — ikili, "beğeni" değil karşılaştırmalı oy) verebilir; bir kullanıcı aynı yayınlanmış piramide yalnızca bir kez oy verebilir (`UNIQUE(ranking_id, user_id)`).
4. **Topluluk özeti:** Bir öznenin (örn. "Zidane") tüm yayınlanmış piramitleri arasında, her katman için "Evet" oranı hesaplanıp gösterilir — örn. *"Topluluğun %72'si Zidane'ı top 10'da görüyor"* (o katmanı yeşil işaretleyen yayınlanmış piramit sayısı ÷ o özne için yayınlanmış toplam piramit sayısı).

## Ödüllendirme (kesin kurallar)
Bu mod bir yarışma **değildir** — Chip veya Rating (ELO) kazandırmaz.
- İlk kez bir özne için piramit **yayınlamak**: **15 XP**.
- Yayınlanmış bir piramide **oy vermek** (agree/disagree): **2 XP** (günde en fazla 10 oy XP kazandırır — spam'i önlemek için).
- Bu XP miktarları, [Level Sistemi](/guide/systems/level-system-avatars)'ndeki "Offline Mod" kazanım mantığına (rakip yokluğunda performansa göre XP) paralel, düşük ama düzenli bir içerik-üretim teşviki olarak tasarlanmıştır.

## Backend İhtiyaçları (uygulanacak şema ve API)
- **`pyramid_rankings` tablosu:** `id`, `user_id` (FK), `subject_type` (`'player'` veya `'team'`), `subject_id`, `layers` (JSON — `{"50": "green", "25": "green", "10": "red"}` gibi), `published` (bool), `created_at`.
- **`pyramid_reactions` tablosu:** `id`, `ranking_id` (FK), `user_id` (FK), `reaction` (`'agree'`/`'disagree'`), `created_at`. `UNIQUE(ranking_id, user_id)` kısıtı.
- `POST /api/game/pyramid-ranking/generate` → `{"subject_type": "player", "subject_id": 123}` gönderilir, sistem yeni bir taslak `pyramid_rankings` satırı oluşturup `ranking_id` döner.
- `POST /api/game/pyramid-ranking/{ranking_id}/vote` → `{"layer": 50, "answer": "yes"|"no"}` — bir katman için oy işler; "no" gelirse üst katmanlar otomatik `"red"` yazılır ve `layers` JSON'ı tamamlanmış sayılır.
- `POST /api/game/pyramid-ranking/{ranking_id}/publish` → `published = true` yapar, +15 XP.
- `POST /api/game/pyramid-ranking/{ranking_id}/react` → `{"reaction": "agree"|"disagree"}`, +2 XP (günlük limit kontrolüyle).
- `GET /api/game/pyramid-ranking/subject/{subject_type}/{subject_id}/community` → o özne için tüm yayınlanmış piramitlerin katman bazlı "Evet" yüzdesini döner.
