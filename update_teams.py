import os
import sys
sys.path.append(os.path.abspath('backend'))

from database import SessionLocal
from models import Team

db = SessionLocal()

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
    ("%Atlético de Madrid%", "Atlético Madrid"),
    ("%Atletico%Madrid%", "Atlético Madrid"),
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
    teams = db.query(Team).filter(Team.name.ilike(pattern)).all()
    for t in teams:
        t.short_name = known_name
        print(f"Updated {t.name} -> {t.short_name}")

db.commit()
db.close()
print("Done")
