# Sosyal Özellikler (Social & Leaderboards)

Oyuncuların birbirleriyle etkileşimini artıracak sosyal ağ özelliklerinin taslak dokümanıdır.

## Arkadaşlık Sistemi (Friendships)
Veritabanındaki `friendships` tablosu halihazırda bu yapı için kurulmuştur.
- **Arkadaş Ekleme:** Oyuncular benzersiz "Kullanıcı Kodları" (Örn: User#1234) üzerinden birbirlerine istek gönderebilir.
- **Özel Maça Davet Etme (Invite):** Arkadaş listesindeki çevrimiçi (Online) kişilere anlık Multiplayer maç isteği (Notification/Push) atılabilir.

## Liderlik Tabloları (Leaderboards)
Oyuncuları rekabete teşvik edecek, global ve lokal sıralama tabloları:
1. **Global ELO Tablosu:** Dünyadaki en yüksek ELO'ya sahip ilk 100 oyuncu.
2. **Haftalık XP Şampiyonları:** Sadece o hafta içerisinde en çok oynayıp en fazla XP kasan oyuncuların listesi. Haftanın birincisine Elmas (Gems) ödülü verilir.
3. **Arkadaşlar Arası Sıralama:** Yalnızca kendi arkadaş grubunuz içerisindeki ELO rekabeti. 

## Kullanıcı Profili Gösteriş (Flexing)
Profil ekranlarında oyuncunun favori kulübü, desteklediği milli takım, bugüne kadar oynadığı maç sayısı ve Win-Rate (Kazanma Oranı) gibi detaylı istatistikler diğer oyuncular tarafından (arkadaş olunduğunda) görüntülenebilecektir.
