# Rank ve ELO Sistemi

Oyundaki asıl rekabeti tetikleyen, oyuncuları yetenek ve bilgi düzeylerine göre birbirleriyle eşleştiren sıralama sistemidir.

## Başlangıç ve ELO Mantığı
- **Başlangıç:** Sisteme kayıt olan her yeni oyuncu **100 Rating (ELO)** puanı ile oyuna başlar.
- **Kazanç/Kayıp:** Sadece Online oynanan maçlarda geçerlidir. Maç bittiğinde kazanan tarafın ELO puanı artarken, kaybeden tarafın ELO puanı azalır. (Satrançtaki klasik ELO algoritması kullanılarak, güçlü birini yendiğinizde daha çok puan kazanırsınız).

## Ligler ve Haftalık Sıfırlama
Sistem, oyuncuları sahip oldukları ELO puanlarına göre çeşitli Kümelere/Liglere ayırır (Örn: Bronz, Gümüş, Altın).
- Her ligin kesin bir **ELO Alt Sınırı** ve **ELO Üst Sınırı** vardır.
- Sistem **haftalık olarak** (Örn: Her Pazar gecesi) ligleri yeniden belirler ve günceller.
- Haftayı kendi liginde (Grubunda) 1. sırada (Lider) bitiren oyunculara sistem tarafından otomatik olarak değerli **Gems (Mücevher)** ödülleri dağıtılır. Bu da oyuncuları ELO kaybetme korkusunu yenip sürekli maç yapmaya teşvik eder.
