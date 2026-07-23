# Özellik: Bildirimler

**Durum:** Kodlanmadı. Ne backend'de ne frontend'de bir bildirim altyapısı var (push, in-app veya e-posta) — bu doküman ne var olduğunu değil, eklenirse nereye oturacağını anlatır.

## Şu An Ne Var (ve Ne Yok)

- Expo push bildirimleri (`expo-notifications`) kurulu değil, `app.json`'da ilgili bir plugin/izin yok.
- Backend'de bildirim göndermek için bir servis/kuyruk yok.
- Uygulama içi bir "bildirim merkezi" (bildirim listesi ekranı, okunmadı sayacı vb.) yok.
- Kullanıcı, sırada beklerken (`join_queue`/`join_chain_lobby`) veya bir maç bittiğinde yalnızca **uygulama açıkken ve o ekrandayken** WebSocket üzerinden anlık geri bildirim alır; uygulama arka plandaysa hiçbir uyarı gelmez.

## Doğal Aday Kullanım Alanları

`taslak_plan.txt`'teki ekonomi sistemlerine bakıldığında, bir bildirim altyapısının en çok fayda sağlayacağı yerler:

1. **Maç bulundu bildirimi** — kullanıcı bir kuyruğa girip uygulamayı arka plana aldığında, rakip bulununca push bildirimi (şu an yalnızca uygulama önplandayken WS mesajıyla haber veriliyor, bkz. [Multiplayer Core](/guide/game-modes/multiplayer-core)).
2. **Günlük seri (streak) hatırlatması** — `taslak_plan.txt`'te belirtilen "7 ve katları günlük oyun oynama streak'i" ödülü henüz kodlanmadı (bkz. [roadmap.md](/roadmap)); kodlanırsa bir hatırlatma bildirimi doğal bir eşlik eder.
3. **Haftalık lig sonucu** — [Rank/ELO](/guide/systems/ranking-elo) sistemindeki haftalık lig yeniden sıralaması henüz kodlanmadı; kodlanırsa "bu hafta ligini X. sırada bitirdin" bildirimi eklenebilir.
4. **Arkadaşlık istekleri** — `routers/social.py`'de arkadaşlık isteği gönderme/kabul etme endpoint'leri zaten var (bkz. [Sosyal & Liderlik Tabloları](/guide/systems/social-leaderboards)) ama bir istek geldiğinde kullanıcıya haber veren bir bildirim yok.

## Bağımlılıklar

Push bildirimi için: `expo-notifications` (frontend) + push token'ı backend'e kaydedecek bir endpoint (`users` tablosuna bir `push_token` kolonu) + bildirim tetikleyecek bir arka plan görevi/servis. Bunların hiçbiri şu an mevcut değil.
