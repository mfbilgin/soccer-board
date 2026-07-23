# Transferlerden Tahmin Modu — "Kariyer İzi"

Kullanıcıların, efsanevi veya aktif futbolcuların transfer (kulüp kariyeri) geçmişlerine bakarak oyuncuyu tahmin etmeye çalıştıkları bir moddur.

::: tip Düzeltildi
Daha önce burada, `career_guess.py`'nin artık var olmayan `PlayerTeamHistory`, `Player.international_caps` ve `Team.known_as`'ı kullandığı için `/generate`'in 500 döndüğü belirtiliyordu. Bu düzeltildi: sorgu artık `PlayerTransfer` (transfer tarihine göre sıralı `to_team_id` zinciri), `PlayerNationalStat.caps` toplamına dayalı bir subquery ve `Team.short_name` kullanıyor. Kiralık tespiti de gerçek veriyle uyumlu hale getirildi: `transfer_fee` alanı Türkçe ("Kiralık"/"Kiralıktan geri döndü") olduğu için kontrol `"kiral" in transfer_fee.lower()` şeklinde yapılıyor.
:::

## Oyun Mantığı
Ekranda sadece bir oyuncunun oynadığı takımlar, transfer sırasına göre gösterilir.

*Örnek Ekran:*
> Sporting CP → Manchester United → Real Madrid → Juventus → Manchester United → Al-Nassr

**Cevap:** Cristiano Ronaldo

## Bulmaca Üretimi (kesin akış, kodda doğrulandı)
1. En az **4 farklı transfer** kaydı olan oyuncular arasından (mevcut kodun `HAVING COUNT(...) >= 4` filtresi korunur), tercihen milli takımda **20'den fazla cap** yapmış (daha "tanınabilir") bir oyuncu rastgele seçilir; böyle biri yoksa şart gevşetilip yalnızca "4+ transfer" koşuluyla seçilir.
2. Seçilen oyuncunun `player_transfers` kayıtları `transfer_date`'e göre artan sırayla çekilir, her adımda `to_team_id` (varış takımı) zincire eklenir.

## Zorluk Seçenekleri (yalnızca offline modda kullanıcı tarafından seçilebilir; online modda her zaman Kolay kullanılır — adillik için)
- **Kolay:** Yıllar (`transfer_date`'in yılı) gösterilir, tüm kulüpler açık.
- **Zor:** Yıl gösterilmez; zincirdeki kulüplerin yarısı (küsuratlıysa aşağı yuvarlanır — örn. 6 kulüplü zincirde 3'ü) baştan "???" gizlenir, her yanlış tahminde bir kulüp daha açılır.

## Online ve Offline Modlar
- **Offline Mod:** Oyuncunun doğru futbolcuyu bulabilmek için **5 tahmin hakkı** vardır. Zor moddaysa her yanlış tahminde bir sonraki gizli kulüp açılır. 5 haktan sonra oyuncu kaybeder, doğru cevap gösterilir.
- **Online Mod (buzzer usulü, [Find Player From Two](/guide/game-modes/find-player-from-two) ile aynı desen):** İki oyuncu eşleşir, aynı anda aynı kariyer zincirini (her zaman Kolay modda: yıllar + tüm kulüpler açık) görür. **45 saniye** içinde doğru futbolcuyu ilk yazan taraf turu kazanır. Kimse bulamazsa berabere biter, oda ücreti iade edilir. Yanlış tahmin gönderen oyuncuya **3 saniyelik** bir cooldown uygulanır (rastgele isim sallamayı önlemek için, [Find Player From Two](/guide/game-modes/find-player-from-two)'daki kuralla aynı).

## Kısıtlamalar ve Uç Durumlar
- **Kiralık (loan) transferler:** Zincire dahil edilir, `is_loan: true` bayrağıyla işaretlenir (frontend bunu `(kiralık)` etiketiyle gösterebilir) — bilgili oyuncu için ekstra ipucu niteliğindedir. Tespit, `player_transfers.transfer_fee` alanında **kodda doğrulandı** gerçek veri Türkçe olduğu için `"kiral"` alt dizesi aranarak yapılır ("Kiralık", "Kiralıktan geri döndü").
- **Eşadlılık:** Arama kutusu [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki `/search` endpoint'iyle aynı fuzzy-arama desenini kullanır; doğum yılı ile disambiguation yapılabilir.
- **Yetersiz veri:** Backend, en az 4 farklı takım geçmişine sahip olmayan oyuncuları bulmaca olarak seçmez.

## Backend Akışı
- `GET /api/game/career-guess/generate` **(kodda doğrulandı, çalışıyor):** Yukarıdaki algoritmayla bir oyuncu seçer; kariyer zincirini (`team_id`, `team_name`, `logo_url`, `transfer_date`, `is_loan`) döner.
- `GET /api/game/career-guess/verify` **(kodda doğrulandı, çalışıyor):** Kullanıcının seçtiği oyuncu ID'sini hedef oyuncu ID'siyle karşılaştırır.
- **(Kodlanmadı)** Online mod için `multiplayer.py`'ye `game_mode: "career_guess"` dalı eklenmesi, [Find Player From Two](/guide/game-modes/find-player-from-two)'daki buzzer handler'ıyla aynı desende bir `career_guess_answer` WebSocket action'ı yazılması gerekir.

## Oynanış Akışı (UI/UX)
`frontend/screens/singleplayer/CareerGuessScreen.js` üzerinden ilerler: kariyer zinciri üstte takım logolarıyla dizilir, altta `SearchModal` ile oyuncu tahmini yapılır. Doğru tahmin animasyonlu bir "doğru!" geri bildirimiyle, yanlış tahmin ise kalan hak sayısının azalmasıyla sonuçlanır.
