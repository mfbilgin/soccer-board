# Veritabanı Yapısı (Database)

Sistemimiz SQLAlchemy ORM kullanılarak yönetilen ilişkisel bir SQLite veritabanına (`football_trivia.db`) dayanır.

## ER Diyagramı

```mermaid
erDiagram
    players ||--o{ player_team_history : "has"
    players ||--o{ player_stats : "has"
    teams ||--o{ player_team_history : "has"
    users ||--o{ friendships : "has"

    players {
        int id PK
        int api_id "Transfermarkt ID"
        string known_as
        string search_name
        boolean is_active
        datetime last_updated
        int international_goals
    }

    teams {
        int id PK
        string name
    }

    player_stats {
        int id PK
        int player_id FK
        string league_name
        string season
        int appearances
        int goals
    }
```

## Önemli Tablolar

### 1. Players Tablosu
Tüm oyuncuların temel kimlik bilgileri, aktiflik durumları (`is_active`) ve Milli Takım performansları burada saklanır.

### 2. Player_Stats Tablosu
Oyuncuların lig ve sezon bazında detaylı performansları. TicTacToe gridindeki "La Liga'da 100 gol atan oyuncu" tarzı zorlu sorular bu tablo üzerinden hesaplanır.

### 3. Player_Team_History Tablosu
Oyuncuların kariyerleri boyunca oynadıkları tüm takımlar. Bir oyuncunun aynı anda hem "Team A" hem de "Team B" ile eşleşmesini (kesişim noktası) bulmak için kullanılır.
