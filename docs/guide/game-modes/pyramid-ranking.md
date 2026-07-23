# Piramit Sıralaması Modu — "Sıralama Görüşü"

Bu mod, bir rekabet veya bilgi yarışması değil, tamamen **fikir belirtme ve topluluk oylaması** amacıyla tasarlanmış eğlenceli bir sosyal moddur.

::: danger Henüz kodlanmadı — isim çakışmasına dikkat
Kodda `pyramid.py` / `PyramidScreen.js` adını taşıyan dosyalar **bu modu değil**, [Top 10 Tahmin](/guide/game-modes/top-10-guess) modunu uyguluyor (tarihsel bir isimlendirme hatası). Burada anlatılan "evet/hayır fikir belirtme piramidi" konsepti için backend'de route, frontend'de ekran veya veritabanında ilgili bir tablo **yok**. Bu sayfa tamamen bir tasarım dokümanıdır.
:::

## Mantık ve Piramit Yapısı
Sistem kullanıcıya tartışmalı bir oyuncu veya takım sunar (Örn: Zinedine Zidane, Galatasaray'ın 2000 kadrosu). Piramit aşağıdan yukarıya doğru şu sıralamalarla daralır: **İlk 50, İlk 25, İlk 10, İlk 5, İlk 3 ve 1. Sıra (Zirve).**

## Oylama Akışı
- Oyuncuya sorulur: *"Zidane, tarihin en iyi 50 oyuncusu arasında mıdır?"*
- Oyuncu "Evet" derse, piramidin en alt (50) katmanı **yeşil** olur, bir üst katman sorulur: *"İlk 25'te midir?"*
- Oyuncu "Hayır" derse o katman **kırmızı** olur ve oylama orada sonlanır; ilk "Hayır"dan sonraki tüm üst katmanlar otomatik olarak kırmızı kabul edilir.
- *Örnek:* Zidane top 50 ✅ → top 25 ✅ → top 10 ❌ → üstü otomatik kırmızı.
- Renk körlüğü erişilebilirliği için katmanlar sadece renkle değil, renk + ikon/desenle çift kodlanmalıdır.

## Yayınlama (Publish) ve Sosyal Katman
Kullanıcı piramidini tamamladıktan sonra, kendi kararını toplulukla paylaşmak üzere yayınlayabilir.
- Yayınlanan piramitlere diğer oyuncular **katılma/beğeni/itiraz** (agree/disagree) verebilir.
- Toplu görüşler bir "topluluk piramidi" oluşturur — örn. *"Topluluğun %72'si Zidane'ı top 10'da görüyor"* gibi toplu istatistikler gösterilebilir.
- Bu içerik, organik paylaşım ve sosyal medyada viral olma potansiyeli taşıyan bir kaynaktır — modun asıl tasarım amacı budur.

## Ödüllendirme
Bu mod bir yarışma **değildir** — Chip veya Rating (ELO) kazandırmaz. Piramit yayınlama ve toplulukla etkileşim (beğeni alma vb.) karşılığında hafif bir **XP** ödülü verilebilir (içerik üretimini teşvik etmek için).

## Olası Backend İhtiyaçları (tasarım aşaması)
Kodlanmaya başlanırsa gerekecek asgari yapı:
- `pyramid_rankings` benzeri yeni bir tablo: `subject_type` (player/team), `subject_id`, `user_id`, `layers` (her katman için evet/hayır/belirsiz), `published`, `created_at`.
- Beğeni/itiraz için ayrı bir `pyramid_reactions` tablosu (`ranking_id`, `user_id`, `reaction`).
- Toplulukların oy dağılımını hesaplayan bir agregasyon endpoint'i (`GET /api/game/pyramid-ranking/{subject_id}/community`).
