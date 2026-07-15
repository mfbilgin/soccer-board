# Backend (FastAPI & WebSockets)

Backend sistemi, yüksek performanslı ve asenkron Python framework'ü olan FastAPI üzerine inşa edilmiştir.

## REST API (routers/)
Tüm HTTP endpoint'leri `routers` klasörü altında mantıksal olarak ayrılmıştır.
- **auth.py:** Kullanıcı kaydı, girişi (JWT tabanlı) işlemlerini barındırır.
- **game.py / tictactoe.py:** Tek oyunculu (Singleplayer) modlarda grid oluşturma, oyuncu tahminlerini doğrulama (Validation) gibi asıl oyun iş mantığını içerir.
- **users.py:** Kullanıcı profili, XP ve Level bilgilerinin getirilmesi.

## Gerçek Zamanlı Eşleşme (socket_manager.py)
Multiplayer tarafı tamamen WebSockets (veya socket.io) altyapısı üzerine kuruludur.
`socket_manager.py` şunlardan sorumludur:
1. **Lobi Yönetimi:** Kullanıcıların odalara (Room) katılması.
2. **Eşleştirme (Matchmaking):** Aynı seviyedeki oyuncuların birbirleriyle eşleştirilmesi.
3. **Oyun Döngüsü Senkronizasyonu:** Bir oyuncu tahtada bir hamle (örneğin X yerleştirdiğinde) yaptığında anında diğer oyuncuya iletilmesi ve tahtanın güncellenmesi.
4. **Zamanlayıcılar (Timers):** Sıra kimdeyse ona ayrılan sürenin backend tarafında güvenli bir şekilde sayılması.
