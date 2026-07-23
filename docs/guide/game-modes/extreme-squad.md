# En 'X' Kadroyu Kur Modu (Extreme Squad) — "Hayalindeki Sınırlı XI"

Bu mod, oyuncunun güncel futbol kadrolarındaki futbolcuların fiziksel özelliklerine (yaş, boy) ne kadar hakim olduğunu ölçen bir kadro mühendisliği oyunudur.

**Durum:** Kodlanmadı. Bu sayfa tam bir uygulama şartnamesidir.

## Dizilim (sabit, tek format)
Kadro her zaman **1-4-3-3** dizilimiyle, toplam **11 slotla** kurulur: 1 Kaleci, 4 Defans, 3 Ortasaha, 3 Forvet.

Rol eşlemesi, veritabanındaki `players.position` alanıyla birebir örtüşür (bu alan yalnızca 5 değer alır): `Goalkeeper` → Kaleci, `Defender` → Defans, `Midfield` → Ortasaha, `Attack` → Forvet. `position = 'Missing'` olan oyuncular hiçbir slota uygun değildir ve aday havuzuna girmez.

## Oyun Amacı ve Hedef
Sistem, optimize edilecek kriteri ve 11 slotun her biri için **spesifik bir takım** belirler; oyuncu her slota, o takımda **şu an aktif** olan ve o slotun rolüne uyan bir futbolcu yerleştirir.

- **Kriter (rastgele seçilir, ikiden biri):** `youngest` (toplam yaş minimum) veya `tallest` (toplam boy maksimum).
- *Örnek Ekran:*
  - Kaleci Slotu → **Milan** (kullanıcı Milan'ın güncel kadrosundan en genç/en uzun kaleciyi bulmaya çalışır)
  - 1. Defans Slotu → **Real Madrid**
  - 2. Defans Slotu → **Fenerbahçe**
  - *(...4 Defans, 3 Ortasaha, 3 Forvet için toplam 11 farklı takım)*

## "Aktiflik" ve "Güncel Takım" Tanımı
"Şu an X takımında aktif" durumu şu sorguyla belirlenir: `players.is_active = true` **ve** o oyuncunun `player_transfers` tablosundaki en güncel `transfer_date`'e sahip `to_team_id`'si = ilgili slotun takımı.

## Kısıtlar ve Oynanış Kuralları
1. **Sistemin Takım Dayatması:** Oyuncu kendi kafasına göre herhangi bir takımdan oyuncu seçemez; her slot için hangi takımdan seçim yapılacağı sistem tarafından belirlenmiştir.
2. **Takım Benzersizliği:** 11 slotun tamamı farklı takımlardan oluşur; aynı takım iki slotta görünmez.
3. **Rol Uyumu:** Bir slota yalnızca o slotun rol kategorisine (`Goalkeeper`/`Defender`/`Midfield`/`Attack`) uyan bir oyuncu yerleştirilebilir.
4. **Zaman Sınırı:** Kullanıcı 90 saniye içinde 11 slotun tamamını doldurmak zorundadır.

## Puanlama ve Kazanma Koşulları
Sistem, verilen 11 takım + rol kısıtıyla kurulabilecek **teorik en iyi kadronun** (her slot için o takımın o roldeki en genç/en uzun aktif oyuncusu) toplam yaş/boy değerini bulmaca üretim anında hesaplar ve saklar. Kullanıcının kurduğu kadronun toplamı bu teorik en iyiyle kıyaslanır; sapma yüzdesi [Stats Target](/guide/game-modes/stats-target) ile aynı 5 kademeli XP tablosuna göre ödüllendirilir:

| Teorik en iyiye sapma | XP | Tier |
|---|---|---|
| %0 (kusursuz) | **25 XP** | 0 |
| ≤ %5 | **25 XP** | 1 |
| ≤ %15 | **15 XP** | 2 |
| ≤ %25 | **10 XP** | 3 |
| > %25 | **5 XP** | 4 |

**Multiplayer (Online) Kazanma Koşulu:**
- İki oyuncu eşleştiğinde ikisinin de ekranına aynı "Hedef" (kriter) ve aynı 11 "Takım Slotu" gelir; her ikisi de 90 saniye içinde kendi kadrosunu doldurmaya çalışır.
- Rakibin hangi slotu kilitlediği (doldurduğu) görülür ama kimi seçtiği görülmez (kör seçim).
- Süre bittiğinde veya iki oyuncu da kilitlediğinde ekran ikiye ayrılır (Showdown). Teorik en iyiye daha yakın kadroyu kuran kazanır.
- **Eşitlik:** İki oyuncu da teorik en iyiye eşit uzaklıktaysa, kadrosunu daha önce kilitleyen kazanır.
- **Eksik/geçersiz kadro:** Süre bitiminde 11 slotun tamamı dolu değilse veya bir slotta rol/takım uyumsuz bir oyuncu varsa, o oyuncu otomatik kaybeder.
- İki taraf da geçersiz/eksikse el berabere biter, oda ücreti iade edilir.

## Backend Sözleşmesi
- `GET /api/games/extreme-squad/generate` → yanıt: `{"puzzle_id": "...", "criterion": "youngest"|"tallest", "slots": [{"slot_id": 0, "role": "Goalkeeper", "team_id": 123, "team_name": "Milan"}, ...11 slot], "theoretical_best": 187.4}`
- `POST /api/games/extreme-squad/validate-single` → `{"slot_id": 0, "player_id": 456}` gönderilir; backend oyuncunun o slotun `team_id`'sinde aktif olup olmadığını (yukarıdaki "Aktiflik" kuralıyla) ve rolünün uyup uymadığını kontrol eder, `{"valid": true, "birth_date": "...", "height_cm": 187}` ya da `{"valid": false, "message": "Bu oyuncu Milan'da aktif değil."}` döner.
- `POST /api/games/extreme-squad/validate` → tüm 11 `player_id`'yi alır, toplamı hesaplar, teorik en iyiyle kıyaslayıp yukarıdaki XP tablosuna göre sonucu döner (`target_score.py`'deki `validate` deseniyle aynı: XP ekleme + level-up kontrolü tek istekte yapılır).

## Ön Koşul: Boy Verisi
`players` tablosunda oyuncu boyu (`height_cm`) alanı yoktur — yalnızca `birth_date` vardır. "En uzun kadro" kriterinin çalışabilmesi için önce `players` tablosuna bir `height_cm` sütunu eklenmesi ve scraper'ın bunu doldurması gerekir. Bu alan eklenene kadar yalnızca `youngest` kriteriyle başlanabilir.
