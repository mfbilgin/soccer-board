# Sıralama ve ELO Sistemi (Ranking)

Oyunun rekabetçi doğasını vurgulayan, kodlanması planlanan Multiplayer dereceli (Ranked) sisteminin tasarım belgesidir.

## ELO Puanlama Mantığı
Satrançtan aşina olduğumuz standart bir ELO puanlama algoritması kullanılacaktır.
- Her yeni kullanıcı 1000 ELO puanıyla başlar.
- Eğer 1000 ELO'luk bir oyuncu, 1500 ELO'luk zorlu bir rakibi yenerse çok daha yüksek puan (Örn: +45) kazanır.
- Kendi seviyesinden çok düşük birine yenilirse ciddi ELO kaybeder (Örn: -40).

## Kümeler ve Rütbeler (Tiers)
Oyuncuların ELO puanlarına göre yerleşecekleri küme sistemi şu şekildedir:
1. **Bronz Lig (Amateur):** 0 - 1199 ELO
2. **Gümüş Lig (Semi-Pro):** 1200 - 1499 ELO
3. **Altın Lig (Pro):** 1500 - 1899 ELO
4. **Elit Lig (World Class):** 1900 - 2499 ELO
5. **Efsane Ligi (Legendary):** 2500+ ELO

Her sezon (örn: ayda bir) ELO puanları belirli bir seviyeye sıfırlanır (Soft Reset) ve oyunculara bitirdikleri lige göre toplu sezon sonu Chips/Gems ödülleri dağıtılır.
