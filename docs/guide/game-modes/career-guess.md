# Transferlerden Tahmin Modu — "Kariyer İzi"

Kullanıcıların, efsanevi veya aktif futbolcuların transfer (kulüp kariyeri) geçmişlerine bakarak oyuncuyu tahmin etmeye çalıştıkları bir moddur.

**Durum:** Singleplayer kodlanmış ve çalışıyor. Online kısmı (aşağıda) henüz kodlanmadı.

## Oyun Mantığı
Ekranda sadece bir oyuncunun oynadığı takımlar, transfer sırasına göre gösterilir.

*Örnek Ekran:*
> Sporting CP → Manchester United → Real Madrid → Juventus → Manchester United → Al-Nassr

**Cevap:** Cristiano Ronaldo

## Bulmaca Üretimi
1. En az **4 farklı transfer** kaydı olan oyuncular arasından, tercihen milli takımda **20'den fazla cap** yapmış (daha "tanınabilir") bir oyuncu rastgele seçilir; böyle biri yoksa şart gevşetilip yalnızca "4+ transfer" koşuluyla seçilir.
2. Seçilen oyuncunun transfer kayıtları tarihe göre artan sırayla çekilir, her adımda varış takımı zincire eklenir.

## Zorluk Seçenekleri (yalnızca offline modda kullanıcı tarafından seçilebilir; online modda her zaman Kolay kullanılır — adillik için)
- **Kolay:** Yıllar gösterilir, tüm kulüpler açık.
- **Zor:** Yıl gösterilmez; zincirdeki kulüplerin yarısı (küsuratlıysa aşağı yuvarlanır — örn. 6 kulüplü zincirde 3'ü) baştan "???" gizlenir, her yanlış tahminde bir kulüp daha açılır.

## Online ve Offline Modlar
- **Offline Mod:** Oyuncunun doğru futbolcuyu bulabilmek için **5 tahmin hakkı** vardır. Zor moddaysa her yanlış tahminde bir sonraki gizli kulüp açılır. 5 haktan sonra oyuncu kaybeder, doğru cevap gösterilir.
- **Online Mod (buzzer usulü, [Find Player From Two](/guide/game-modes/find-player-from-two) ile aynı desen):** İki oyuncu eşleşir, aynı anda aynı kariyer zincirini (her zaman Kolay modda: yıllar + tüm kulüpler açık) görür. **45 saniye** içinde doğru futbolcuyu ilk yazan taraf turu kazanır. Kimse bulamazsa berabere biter, oda ücreti iade edilir. Yanlış tahmin gönderen oyuncuya 3 saniyelik bir cooldown uygulanır (rastgele isim sallamayı önlemek için).

## Kısıtlamalar ve Uç Durumlar
- **Kiralık (loan) transferler:** Zincire dahil edilir, `is_loan: true` bayrağıyla işaretlenir (frontend bunu `(kiralık)` etiketiyle gösterebilir) — bilgili oyuncu için ekstra ipucu niteliğindedir. Kiralık tespiti, transfer bedeli metninde "kiral" alt dizesi aranarak yapılır (veri Türkçe: "Kiralık", "Kiralıktan geri döndü").
- **Eşadlılık:** Arama kutusu [TicTacToe](/guide/game-modes/tictactoe-4x4)'daki `/search` endpoint'iyle aynı fuzzy-arama desenini kullanır; doğum yılı ile disambiguation yapılabilir.
- **Yetersiz veri:** En az 4 farklı takım geçmişine sahip olmayan oyuncular bulmaca olarak seçilmez.

## Backend Sözleşmesi
- `GET /api/game/career-guess/generate`: Yukarıdaki algoritmayla bir oyuncu seçer; kariyer zincirini (`team_id`, `team_name`, `logo_url`, `transfer_date`, `is_loan`) döner.
- `GET /api/game/career-guess/verify`: Kullanıcının seçtiği oyuncu ID'sini hedef oyuncu ID'siyle karşılaştırır.
- Online mod için multiplayer oda başlatma akışına `game_mode: "career_guess"` dalı, [Find Player From Two](/guide/game-modes/find-player-from-two)'daki buzzer handler'ıyla aynı desende bir `career_guess_answer` WebSocket action'ı eklenir.

## Oynanış Akışı (UI/UX)
`frontend/screens/singleplayer/CareerGuessScreen.js` üzerinden ilerler: kariyer zinciri üstte takım logolarıyla dizilir, altta arama modalıyla oyuncu tahmini yapılır. Doğru tahmin animasyonlu bir "doğru!" geri bildirimiyle, yanlış tahmin ise kalan hak sayısının azalmasıyla sonuçlanır.
