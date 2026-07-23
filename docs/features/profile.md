# Özellik: Profil

**Durum:** Kodlanmadı — yalnızca alt sekme (tab) olarak yer tutucu var.

## Şu An Ne Var

`App.js`'teki `MainTabs`, beş alt sekme tanımlar: **Oyna** (gerçek ekran — `HomeScreen`), **Sıralama**, **Market**, **Sosyal**, **Profil**. Sonuncusu dahil dördü şu an `DummyScreen` (boş, tek renkli bir `View`) render ediyor:

```js
<Tab.Screen name="Profil" component={DummyScreen} />
```

Kullanıcının "profil" sayılabilecek verisi (chip, gem, xp, level, rating) zaten `GET /api/auth/me` ile erişilebilir durumda ve `HomeScreen`, `LobbyScreen`, `RoomSelectionScreen` gibi ekranlarda parça parça (örn. sadece chip sayısı bir para birimi rozetinde) gösteriliyor — ama tüm bu bilgiyi bir arada gösteren, avatarı olan, geçmiş maçları listeleyen ayrı bir "Profil" ekranı yok.

## Yapılacaklar (bkz. [roadmap.md](/roadmap))

`taslak_plan.txt`'teki orijinal tasarıma göre bir Profil ekranının kapsayacağı özellikler:
- Avatar özelleştirme (forma/atkı/kramponşapka gibi kozmetik öğeler; gems/chips ile marketten satın alınır, her 10/15 seviyede bir de ödül olarak kazanılır) — bkz. [Level & Avatar Sistemi](/guide/systems/level-system-avatars).
- Chip/gem/xp/level/rating'in tek bir yerde toplu gösterimi (şu an dağınık).
- Maç geçmişi / istatistikler (backend'de `match_logs/` altında JSONL formatında maç logları zaten tutuluyor — bkz. `routers/multiplayer.py`'deki `log_match_event` — ama bunları kullanıcıya gösteren bir arayüz yok).

## Bağımlılıklar

Backend tarafında ek bir endpoint gerekmez (mevcut `/api/auth/me` yeterli) — eksik olan yalnızca frontend ekranıdır. Avatar/market özelliği için ise backend'de yeni bir "envanter" tablosu ve satın alma endpoint'i gerekecektir (henüz yok).
