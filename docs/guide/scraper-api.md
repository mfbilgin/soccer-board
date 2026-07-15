# Scraper ve Veri Güncelleme (Scraper API)

Uygulamanın kalbi, güncel futbol istatistiklerinin çekildiği **Transfermarkt API (TMAPI)** altyapısına dayanır.

## TMAPI (performance-game)
Kullandığımız asıl endpoint, bir oyuncunun tüm kariyer maçlarını tek seferde dönen `performance-game` uç noktasıdır:
`https://tmapi.transfermarkt.technology/player/{id}/performance-game`

Bu endpoint bize oyuncunun:
- Sahada kalma süresini (`participationState`)
- Gol ve asistlerini
- Gördüğü kartları
- Oynadığı turnuvaları liste olarak verir.

## full_scraper.py (Tam Tarama)
Projenin ilk kurulumunda çalıştırılır. Hazır bir id listesinden (`Kaggle veri seti vb.`) başlar ve oyuncuların tüm istatistiklerini sıfırdan veritabanına gömer.
- **Güvenlik Filtresi:** Sadece `participationState == 'played'` olan maçlar sayılır. Yedek kalınan veya sakatlık dönemi maçları istatistiklere eklenmez.
- **Hazırlık Maçı Filtresi:** `competitionId == "FS"` olan dostluk maçları asla resmi istatistik kabul edilmez.

## daily_updater.py (Kısmi Delta Tarama)
Sistemin sürdürülebilirliği için tasarlanmıştır. Her gün 47.000 oyuncuyu taramak imkansız olduğundan, sadece `is_active = True` olan ve son 24 saattir güncellenmemiş oyuncuları günceller.
- Bir oyuncunun en son kaydı 2024 ve sonrası sezonlara aitse `is_active` otomatik olarak `True` kalır. Emekli oyuncular bir daha asla taranmaz.
