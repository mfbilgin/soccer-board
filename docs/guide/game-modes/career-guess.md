# Transferlerden Tahmin Modu — "Kariyer İzi"

Kullanıcıların, efsanevi veya aktif futbolcuların transfer (kulüp kariyeri) geçmişlerine bakarak oyuncuyu tahmin etmeye çalıştıkları bir moddur.

::: danger Şu an production'da çalışmıyor
`backend/routers/career_guess.py`, `models.py`'de artık var olmayan `PlayerTeamHistory` sınıfını, `Player.international_caps` alanını ve `Team.known_as` alanını kullanıyor. Bu üçü de `models.py`'nin V1→V2 şema geçişinde kaldırıldı/yeniden adlandırıldı (bkz. [Database Structure](/guide/database)). Sonuç: `/api/game/career-guess/generate` çağrıldığında backend `AttributeError` ile 500 döner — mod şu an oynanamıyor.

**Önerilen düzeltme (henüz uygulanmadı):**
- `models.PlayerTeamHistory` → `models.PlayerTransfer` (oyuncunun `to_team_id`'lerini `transfer_date`'e göre sıralayarak kariyer zincirini kur).
- `Player.international_caps > 20` filtresi → `models.PlayerNationalStat.caps` üzerinden bir subquery (aynı oyuncunun milli takım cap toplamı).
- `Team.known_as` → `Team.short_name`.
- Eski model `start_year`/`end_year` (bir kulüpte kalınan süre) veriyordu; `PlayerTransfer` bunun yerine tek bir `transfer_date` (transfer tarihi) tutuyor — zincir gösterimi buna göre uyarlanmalı (`start_year` yerine sadece transfer yılı gösterilebilir).
:::

## Oyun Mantığı
Ekranda sadece bir oyuncunun oynadığı takımlar, transfer sırasına göre gösterilir. Opsiyonel olarak, oyuncunun o takıma katıldığı **yıl** bilgisi de ipucu olarak yer alabilir (zorluk ayarı — bkz. aşağı).

*Örnek Ekran:*
> Sporting CP → Manchester United → Real Madrid → Juventus → Manchester United → Al-Nassr

**Cevap:** Cristiano Ronaldo

## Zorluk Seçenekleri
- **Kolay:** Yıllar gösterilir, tüm kulüpler açık.
- **Zor:** Yıl gösterilmez; bazı kulüpler "???" olarak gizlenir, her yanlış tahminde bir kulüp daha açılır (tek oyunculuda hak başına bir ipucu).

## Online ve Offline Modlar
- **Offline Mod:** Oyuncunun doğru futbolcuyu bulabilmek için **5 tahmin hakkı** vardır. Her yanlış tahminde sistem küçük bir ekstra ipucu verebilir (zor modda bir sonraki gizli kulübü açar). 5 haktan sonra oyuncu kaybeder.
- **Online Mod:** İki oyuncu aynı anda aynı kariyer geçmişini görür. Doğru futbolcuyu sisteme ilk giren oyuncu kazanır. Kimse bulamazsa (süre dolarsa) el berabere biter ve oda ücreti iade edilir (bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)).

## Kısıtlamalar ve Uç Durumlar
- **Kiralık (loan) transferler:** Zincire dahil edilir, `(loan)` etiketiyle işaretlenir — bilgili oyuncu için ekstra ipucu niteliğindedir.
- **Eşadlılık:** Arama kutusu autocomplete ile resmi ismi seçtirir; doğum yılı ile disambiguation yapılabilir.
- **Yetersiz veri:** Backend, en az 4 farklı takım geçmişine sahip olmayan oyuncuları bulmaca olarak seçmez (mevcut kodda `HAVING COUNT(...) >= 4` filtresi böyle çalışıyor, düzeltmeden sonra da korunmalı).

## Backend Akışı (düzeltildikten sonra hedeflenen)
- `GET /api/game/career-guess/generate`: En az 4 transferi olan, tercihen milli takımda da çok sayıda cap yapmış (daha "tanınabilir") bir oyuncuyu rastgele seçer; kariyer zincirini (`team_id`, `short_name`, `logo_url`, `transfer_date`) döner.
- `GET /api/game/career-guess/verify`: Kullanıcının seçtiği oyuncu ID'sini hedef oyuncu ID'siyle karşılaştırır.

## Oynanış Akışı (UI/UX)
`frontend/screens/singleplayer/CareerGuessScreen.js` üzerinden ilerler: kariyer zinciri üstte takım logolarıyla dizilir, altta `SearchModal` ile oyuncu tahmini yapılır. Doğru tahmin animasyonlu bir "doğru!" geri bildirimiyle, yanlış tahmin ise kalan hak sayısının azalmasıyla sonuçlanır.
