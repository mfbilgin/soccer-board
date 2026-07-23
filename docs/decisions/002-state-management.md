# ADR 002 — Frontend State Yönetimi: Küresel Store Yok

**Durum:** Kabul edildi (fiilen — hiçbir ekranda Redux/Context/Zustand/Recoil kullanılmıyor).

## Bağlam

Uygulama çoğunlukla bağımsız ekranlardan oluşuyor: bir singleplayer bulmaca ekranı kendi bulmacasını çeker, bir multiplayer ekranı kendi WebSocket akışını yönetir. Ekranlar arasında paylaşılması gereken veri sınırlı: esas olarak "giriş yapmış kullanıcının profili" (chip/gem/xp/level/rating) ve WebSocket bağlantısının kendisi.

## Karar

- **Küresel bir state kütüphanesi (Redux, Context API, Zustand, Recoil, ...) kullanılmıyor.**
- Her ekran kendi verisini kendi `useState`/`useEffect`'iyle yönetir; ihtiyaç duyduğunda `GET /api/auth/me` ile kullanıcı profilini kendi başına çeker (`LobbyScreen`, `RoomSelectionScreen`, her `Multiplayer*Screen`, `SingleplayerScreen` bunu bağımsız bağımsız yapar).
- Kalıcı olması gereken tek şey — JWT — küresel bir state'te değil, `expo-secure-store`'da (cihaz düzeyinde, React state'inin dışında) tutulur.
- Gerçek zamanlı oyun durumu (WebSocket'ten gelen `game_state`) bir store'a yazılmaz; `SocketService.on(type, callback)` ile doğrudan ilgili ekranın yerel state'ine akar. `SocketService`'in kendisi modül-seviyesinde tekil (singleton) bir nesnedir — bu, "küresel state yok" kuralının kasıtlı tek istisnasıdır, çünkü WebSocket bağlantısının kendisi (state değil, bir *bağlantı*) ekranlar arasında paylaşılmak zorundadır.

## Sonuçlar

- ✅ Yeni bir ekran/mod eklemek düşük sürtünmeli: bir store'a action/reducer/selector eklemeye gerek yok, ekran kendi state'ini yönetir (bu session'da 6 yeni mod bu şekilde hızla eklendi).
- ✅ Ekranlar birbirinden bağımsız test edilebilir/anlaşılabilir; bir ekranı okumak için başka bir yerdeki store tanımına bakmaya gerek yok.
- ⚠️ **Kullanıcı profili tekrar tekrar, birbirinden habersiz şekilde çekiliyor.** Kullanıcı Lobby → RoomSelection → MultiplayerXScreen şeklinde ilerlerken üç ayrı `GET /api/auth/me` isteği atılır; chip harcandıktan hemen sonra bir önceki ekranın state'i güncel değildir (örn. RoomSelection'da görünen chip sayısı, bir odaya girip çıktıktan sonra yeniden yüklenmeden güncellenmez). Şu an gözlemlenen ama henüz sorun yaratmayan bir tutarsızlık kaynağı.
- Ekranlar arasında veri geçişi React Navigation'ın `route.params`'ı ile yapılır (örn. `navigation.navigate('MultiplayerExtremeSquad', { tier })`) — bu da küresel state'in yerini kısmen tutar ama yalnızca doğrudan komşu ekranlar arasında çalışır.
- İleride bir "kullanıcı profili" küresel state'i (hafif bir Context ile) eklenirse, bunun kapsamı yalnızca `/api/auth/me` sonucunu önbelleklemek olmalı — WebSocket oyun durumunu küreselleştirmek bu ADR'ın ele aldığı sorunun dışındadır ve önerilmez.
