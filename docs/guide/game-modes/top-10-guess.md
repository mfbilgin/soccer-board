# Top 10 Tahmin Modu — "İlk 10 Listesi"

Bir ligde/milli takımda/kulüpte tüm zamanların bir metrikte (gol, asist veya maç sayısı) **ilk 10** futbolcusunu tahmin etmeye dayanan bir hafıza ve bilgi yarışmasıdır.

::: tip Uygulama durumu ve isimlendirme notu
Bu mod kodda **`backend/routers/pyramid.py`** (`/api/game/pyramid/generate`) ve **`frontend/screens/singleplayer/PyramidScreen.js`** olarak yaşıyor — isim tarihsel bir nedenle "Pyramid" kalmış, ama gerçekte uyguladığı oyun tam olarak burada anlatılan Top 10 modudur (3 can, ilk 3 açık, "Bu oyuncu ilk 10'da değil" mesajı). [Piramit Sıralaması](/guide/game-modes/pyramid-ranking) sayfasındaki farklı (evet/hayır fikir belirtme) mod ise ayrı bir konsepttir ve **henüz kodlanmamıştır** — iki dosyayı birbirine karıştırmayın.
:::

## Arayüz ve Kurallar
- Oyun ekranında alt alta dizilmiş **10 kutucuk** bulunur.
- İlk 3 kutucuk (sıralamadaki ilk 3 kişi) ipucu niteliğinde dolu olarak gelir.
- Oyuncuların **3 yanlış yapma hakkı** vardır. 3 kere yanlış tahmin eden oyunu kaybeder; kalan hepsi "kaçırıldı" olarak kırmızıyla açılır.

## Liste Türleri (mevcut backend'de rastgele seçilir)
`pyramid.py`'deki `generate_pyramid` üç farklı liste türünden birini rastgele üretir:
1. **Kulüp Ligi:** Rastgele bir lig (Premier League, La Liga, Serie A, Ligue 1, Bundesliga, Süper Lig) + rastgele bir metrik (gol/asist/maç) — "Premier League'de En Çok Gol Atanlar" gibi.
2. **Milli Takım:** Milli takımlarda en çok gol atanlar listesi.
3. **Takım Bazlı:** Belirli bir popüler kulüp (Real Madrid, Barcelona, Fenerbahçe vb.) formasıyla en çok gol/asist/maç yapanlar.

## Offline (Tek Oyunculu) Mod
- Oyuncu, eksik olan 7 sırayı tahmin etmeye çalışır.
- Yanlış haklarını doldurmadan listedeki tüm oyuncuları tamamlarsa kazanır. Yarışma baskısı yoktur.

## Online (Multiplayer) Mod
::: warning Henüz multiplayer ekranı yok
`frontend/screens/multiplayer/` altında bu mod için bir ekran bulunmuyor — aşağıdaki online akış GDD'deki tasarım hedefidir, henüz kodlanmadı.
:::
- İki veya daha fazla oyuncu aynı tahta üzerinde **sırayla** tahmin yapar.
- **Puanlama:** Bir oyuncu doğru tahmin yaptığında, bulduğu futbolcunun **sıra numarası kadar puan** kazanır — yani 10. sıradaki (en az bilinen) futbolcuyu bilen 10 puan, 1. sıradaki (en tanınmış) futbolcuyu bilen sadece 1 puan alır. Alt sıralar daha zor olduğu için daha çok puan getirir.
- Bir oyuncu tahmin edemezse veya süresi biterse sıra diğerine geçer.
- Tablo tamamlandığında en çok puanı toplayan kişi maçın galibi olur.

## Kısıtlamalar ve Uç Durumlar
- **Sıra tahmini istenmez:** Oyuncu yalnızca ismi yazar; sistem doğru sıraya otomatik yerleştirir — hangi sırada olduğunu bilmek zorunda değildir, bu sürtünmeyi azaltır.
- **Eşadlılık:** Autocomplete ile resmi isim seçtirilir.
- **Veri yeterliliği:** Backend, seçilen lig/takım/kategori için en az 10 oyuncu bulamazsa (`len(top_players) < 10`) `500` hatası döner — bu durumda frontend yeni bir liste istemelidir.
- **Liste güncelliği:** "Tüm zamanlar" listeleri, veritabanındaki `player_club_stats`/`player_national_stats` toplamlarının doğruluğuna bağlıdır.
