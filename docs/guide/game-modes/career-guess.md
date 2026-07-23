# Transferlerden Tahmin Modu — "Kariyer İzi"

Kullanıcıların, efsanevi veya aktif futbolcuların transfer (kulüp kariyeri) geçmişlerine bakarak oyuncuyu tahmin etmeye çalıştıkları bir moddur.

::: danger Singleplayer şu an production'da çalışmıyor
`backend/routers/career_guess.py`, `models.py`'de artık var olmayan `PlayerTeamHistory` sınıfını, `Player.international_caps` alanını ve `Team.known_as` alanını kullanıyor. Bu üçü de `models.py`'nin V1→V2 şema geçişinde kaldırıldı/yeniden adlandırıldı (bkz. [Database Structure](/guide/database)). Sonuç: `/api/game/career-guess/generate` çağrıldığında backend `AttributeError` ile 500 döner — mod şu an oynanamıyor.

**Kesin düzeltme:**
- `models.PlayerTeamHistory` → `models.PlayerTransfer` (oyuncunun `to_team_id`'lerini `transfer_date`'e göre sıralayarak kariyer zincirini kur; eski model bir kulüpte kalınan `start_year`/`end_year` aralığı veriyordu, `PlayerTransfer` yerine tek bir `transfer_date` verir — zincir gösterimi buna göre uyarlanmalı, yalnızca transfer yılı gösterilir).
- `Player.international_caps > 20` filtresi → `db.query(func.sum(models.PlayerNationalStat.caps)).filter(...).scalar()` ile hesaplanan bir subquery.
- `Team.known_as` → `Team.short_name`.
:::

## Oyun Mantığı
Ekranda sadece bir oyuncunun oynadığı takımlar, transfer sırasına göre gösterilir.

*Örnek Ekran:*
> Sporting CP → Manchester United → Real Madrid → Juventus → Manchester United → Al-Nassr

**Cevap:** Cristiano Ronaldo

## Bulmaca Üretimi (düzeltildikten sonra kesin akış)
1. En az **4 farklı transfer** kaydı olan oyuncular arasından (mevcut kodun `HAVING COUNT(...) >= 4` filtresi korunur), tercihen milli takımda **20'den fazla cap** yapmış (daha "tanınabilir") bir oyuncu rastgele seçilir; böyle biri yoksa şart gevşetilip yalnızca "4+ transfer" koşuluyla seçilir.
2. Seçilen oyuncunun `player_transfers` kayıtları `transfer_date`'e göre artan sırayla çekilir, her adımda `to_team_id` (varış takımı) zincire eklenir.

## Zorluk Seçenekleri (yalnızca offline modda kullanıcı tarafından seçilebilir; online modda her zaman Kolay kullanılır — adillik için)
- **Kolay:** Yıllar (`transfer_date`'in yılı) gösterilir, tüm kulüpler açık.
- **Zor:** Yıl gösterilmez; zincirdeki kulüplerin yarısı (küsuratlıysa aşağı yuvarlanır — örn. 6 kulüplü zincirde 3'ü) baştan "???" gizlenir, her yanlış tahminde bir kulüp daha açılır.

## Online ve Offline Modlar
- **Offline Mod:** Oyuncunun doğru futbolcuyu bulabilmek için **5 tahmin hakkı** vardır. Zor moddaysa her yanlış tahminde bir sonraki gizli kulüp açılır. 5 haktan sonra oyuncu kaybeder, doğru cevap gösterilir.
- **Online Mod (buzzer usulü, [Find Player From Two](/guide/game-modes/find-player-from-two) ile aynı desen):** İki oyuncu eşleşir, aynı anda aynı kariyer zincirini (her zaman Kolay modda: yıllar + tüm kulüpler açık) görür. **45 saniye** içinde doğru futbolcuyu ilk yazan taraf turu kazanır. Kimse bulamazsa berabere biter, oda ücreti iade edilir. Yanlış tahmin gönderen oyuncuya **3 saniyelik** bir cooldown uygulanır (rastgele isim sallamayı önlemek için, [Find Player From Two](/guide/game-modes/find-player-from-two)'daki kuralla aynı).

## Kısıtlamalar ve Uç Durumlar
- **Kiralık (loan) transferler:** Zincire dahil edilir, `(loan)` etiketiyle işaretlenir — bilgili oyuncu için ekstra ipucu niteliğindedir. (`player_transfers.transfer_fee` alanında "loan"/"kiralık" geçen kayıtlar bu etiketle işaretlenir.)
- **Eşadlılık:** Arama kutusu [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki `/search` endpoint'iyle aynı fuzzy-arama desenini kullanır; doğum yılı ile disambiguation yapılabilir.
- **Yetersiz veri:** Backend, en az 4 farklı takım geçmişine sahip olmayan oyuncuları bulmaca olarak seçmez.

## Backend Akışı (düzeltildikten sonra hedeflenen)
- `GET /api/game/career-guess/generate`: Yukarıdaki algoritmayla bir oyuncu seçer; kariyer zincirini (`team_id`, `short_name`, `logo_url`, `transfer_date`) döner.
- `GET /api/game/career-guess/verify`: Kullanıcının seçtiği oyuncu ID'sini hedef oyuncu ID'siyle karşılaştırır.
- Online mod için `multiplayer.py`'ye `game_mode: "career_guess"` dalı eklenmesi, [Find Player From Two](/guide/game-modes/find-player-from-two)'daki buzzer handler'ıyla aynı desende bir `career_guess_answer` WebSocket action'ı yazılması gerekir.

## Oynanış Akışı (UI/UX)
`frontend/screens/singleplayer/CareerGuessScreen.js` üzerinden ilerler: kariyer zinciri üstte takım logolarıyla dizilir, altta `SearchModal` ile oyuncu tahmini yapılır. Doğru tahmin animasyonlu bir "doğru!" geri bildirimiyle, yanlış tahmin ise kalan hak sayısının azalmasıyla sonuçlanır.
