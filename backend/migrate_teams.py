import sqlite3

def run_migration():
    conn = sqlite3.connect('c:/Users/PC/Desktop/project/football_trivia.db')
    cursor = conn.cursor()

    # 1. Add known_as column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE teams ADD COLUMN known_as VARCHAR;")
        print("Sütun eklendi: known_as")
    except sqlite3.OperationalError as e:
        print(f"Sütun zaten var veya hata: {e}")

    # 2. Map Elite Clubs
    elite_clubs = [
        ("%Internazionale Milano%", "Inter"),
        ("%Associazione Calcio Milan%", "Milan"),
        ("%Real Madrid%", "Real Madrid"),
        ("Futbol Club Barcelona", "Barcelona"),
        ("Barcelona", "Barcelona"),
        ("Galatasaray%", "Galatasaray"),
        ("Fenerbah%", "Fenerbahçe"),
        ("Be_ikta%", "Beşiktaş"),
        ("Manchester United%", "Manchester United"),
        ("Manchester City%", "Manchester City"),
        ("Arsenal%", "Arsenal"),
        ("Chelsea%", "Chelsea"),
        ("Liverpool%", "Liverpool"),
        ("Juventus%", "Juventus"),
        ("%Bayern M_nchen%", "Bayern Munich"),
        ("Bayern Munich", "Bayern Munich"),
        ("%Paris Saint-Germain%", "PSG"),
        ("%Paris Saint Germain%", "PSG"),
        ("%Atltico%Madrid%", "Atlético Madrid"),
        ("%Atl_tico%Madrid%", "Atlético Madrid"),
        ("Borussia Dortmund", "Borussia Dortmund"),
        ("Tottenham Hotspur%", "Tottenham Hotspur"),
        ("Societ_ Sportiva Calcio Napoli", "Napoli"),
        ("Napoli", "Napoli"),
        ("Associazione Sportiva Roma", "Roma"),
        ("AS Roma", "Roma"),
        ("Aston Villa%", "Aston Villa"),
        ("Newcastle United%", "Newcastle United"),
        ("Bayer 04 Leverkusen", "Bayer Leverkusen"),
        ("RB Leipzig", "RB Leipzig"),
        ("Olympique Lyonnais", "Lyon"),
        ("Olympique de Marseille", "Marseille"),
        ("Sport Lisboa e Benfica", "Benfica"),
        ("Futebol Clube do Porto", "Porto"),
        ("Sporting Clube de Portugal", "Sporting CP"),
        ("Amsterdamsche Football Club Ajax", "Ajax"),
        ("PSV Eindhoven", "PSV")
    ]

    for pattern, known_name in elite_clubs:
        cursor.execute(
            "UPDATE teams SET known_as = ? WHERE name LIKE ?", 
            (known_name, pattern)
        )

    conn.commit()
    
    cursor.execute("SELECT name, known_as FROM teams WHERE known_as IS NOT NULL LIMIT 50;")
    results = cursor.fetchall()
    print("Güncellenen bazı takımlar:")
    for r in results:
        print(f"{r[0]} -> {r[1]}")

    conn.close()

if __name__ == "__main__":
    run_migration()
