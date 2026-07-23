# Şu Anki Durum (Current Task)

::: warning Bu sayfa zamanla eskir
Diğer tüm dokümanların aksine bu sayfa "timeless spec" değildir — belirli bir anın anlık görüntüsüdür. Güncelliğini kontrol etmek için `git log` ve arka plandaki backfill script'lerinin loglarına (`backend/*.log`) bakın. Kalıcı öncelikler için [roadmap.md](/roadmap)'a bakın.
:::

**Son güncelleme:** Bu oturumda, takım isimleri karmaşasının giderilmesinin ardından 6 yeni oyun modu (Chain Reaction, Extreme Squad, Find Player From Two, Flag Eleven, Initials Guess, Top 10'un online kısmı) tamamlandı, commit'lendi, GitHub'a pushlandı ve EAS OTA ile `production` kanalına yayınlandı.

## Şu An Ne Yapılıyor

Arka planda iki idempotent backfill script'i (bkz. [architecture/database.md](/architecture/database)) çalışıyor, ikisi de production Postgres'e yazıyor:

1. **`backend/scripts/backfill_team_profiles.py`** — placeholder isimli (`"Team 12345"`) ve/veya ülke bilgisi eksik takımları TMAPI'den onarıyor. ~29.206 takımdan işleniyor.
2. **`backend/scripts/backfill_player_heights.py`** — `height_cm IS NULL` olan oyuncuları TMAPI'nin `/player/{id}` uç noktasından dolduruyor. ~47.701 oyuncudan işleniyor. Bu tamamlanana kadar Extreme Squad'ın `tallest` kriteri sınırlı takım kapsamasıyla çalışıyor, yetersiz kalırsa otomatik `youngest`'e düşüyor (bkz. `routers/extreme_squad.py`'deki `generate_puzzle` fallback mantığı).

Her ikisi de kesintiye dayanıklı (`WHERE ... IS NULL` gibi bir koşulla çalıştıkları için yarıda kesilse bile güvenle tekrar başlatılabilir).

## Sonraki Adım

1. İki backfill de bitince, takım-isimleri planının doğrulama adımlarını çalıştır:
   - SQL sayıları: placeholder isim sayısı (`name ~ '^Team [0-9]+$'`) ve `country IS NULL` sayısı sıfıra yakın olmalı.
   - "Arsenal" `short_name` çakışması spot-check'i (27 satırdan ~1 satıra düşmeli).
   - Uygulamada manuel arama testi (TicTacToe SearchModal'da "Arsenal" arayıp ülke alt-başlıklarının artık ayırt edici olduğunu doğrula).
   - Pyramid modunun `mode==2` yolunun artık Milan'da 500 vermediğini doğrula.
   - Scraper'ın self-heal davranışını (placeholder bir takıma sahip bilinen bir oyuncu aralığıyla `distributed_scraper.py` çalıştırarak) doğrula.
2. Yeni 6 modun gerçek cihaz/emülatörde manuel testi (şu an yalnızca sunucu tarafında salt-okunur mantık testleriyle doğrulandı; uçtan uca UI testi yapılmadı).

## Bilinen Sorunlar (bu anlık görüntüde)

- `LoginScreen.js` ağ hatasıyla yanlış şifreyi aynı mesajla gösteriyor (bkz. [features/authentication.md](/features/authentication)).
- `security.py`'deki `SECRET_KEY` hardcoded (bkz. [ADR 001](/decisions/001-auth)).
- `flag_eleven.py`'nin `PUZZLES` önbelleği ve benzer modül-seviyesi cache'ler TTL'siz büyüyor (bkz. [architecture/backend.md](/architecture/backend)).
- Yeni 6 modun online kısımları için otomatik test yok; yalnızca elle yazılmış, salt-okunur betiklerle (prod verisine karşı) motor mantığı doğrulandı.
