import sqlite3
from unidecode import unidecode

def run_migration():
    conn = sqlite3.connect('c:/Users/PC/Desktop/project/football_trivia.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE players ADD COLUMN search_name VARCHAR;")
        print("Sütun eklendi: players.search_name")
    except sqlite3.OperationalError:
        print("Sütun zaten var: players.search_name")
        
    try:
        cursor.execute("ALTER TABLE teams ADD COLUMN search_name VARCHAR;")
        print("Sütun eklendi: teams.search_name")
    except sqlite3.OperationalError:
        print("Sütun zaten var: teams.search_name")

    print("Oyuncu isimleri dönüştürülüyor (Unaccenting)...")
    cursor.execute("SELECT id, known_as FROM players")
    players = cursor.fetchall()
    
    player_updates = []
    for pid, name in players:
        if name:
            normalized = unidecode(name).lower()
            player_updates.append((normalized, pid))
            
    cursor.executemany("UPDATE players SET search_name = ? WHERE id = ?", player_updates)
    print(f"{len(player_updates)} oyuncu güncellendi.")

    print("Takım isimleri dönüştürülüyor (Unaccenting)...")
    cursor.execute("SELECT id, name, known_as FROM teams")
    teams = cursor.fetchall()
    
    team_updates = []
    for tid, name, known_as in teams:
        target_name = known_as if known_as else name
        if target_name:
            normalized = unidecode(target_name).lower()
            team_updates.append((normalized, tid))
            
    cursor.executemany("UPDATE teams SET search_name = ? WHERE id = ?", team_updates)
    print(f"{len(team_updates)} takım güncellendi.")

    conn.commit()
    conn.close()
    print("İşlem tamamlandı!")

if __name__ == "__main__":
    run_migration()
