"""
Takim isimlerini (teams.short_name) temizler.

- Genel kurumsal ekleri (S.A.D., F.C., A.S., Spor Kulubu, U19 vb.) regex ile siler.
- Populer kulupler icin elle belirlenmis kisa isimleri (Real Madrid, Fenerbahce,
  PSG, Besiktas...) her seferinde uzerine yazar.
- Idempotent'tir: tum takimlari her calistiginda yeniden isler, sadece degisen
  satirlari commit'ler. Bu yuzden guvenle tekrar tekrar calistirilabilir.

Hangi veritabanina yazacagi backend/.env icindeki DATABASE_URL_V2'ye baglidir
(bkz. backend/.env.example). Production Postgres'e yazmadan once o degerin
dogru oldugundan emin ol.

Kullanim:
    cd backend && ..\\venv\\Scripts\\python.exe scripts/clean_team_names.py
"""
import os
import re
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import Team
from sqlalchemy import text

SUFFIX_PATTERNS = [
    r'\bS\.A\.D\.\b', r'\bS\. A\. D\.\b', r'\bS\.A\.D\b',
    r'\bF\.C\.\b', r'\bFC\b', r'\bFootball Club\b', r'\bFutbol Club\b',
    r'\bC\.F\.\b', r'\bCF\b', r'\bClub de F[úu]tbol\b', r'\bClub de Ftbol\b',
    r'\bA\.C\.\b', r'\bAC\b', r'\bAssociazione Calcio\b',
    r'\bA\.S\.\b', r'\bAS\b', r'\bAssociazione Sportiva\b',
    r'\bS\.S\.\b', r'\bSS\b', r'\bSociet[àa] Sportiva\b', r'\bSociet Sportiva\b',
    r'\bSpor Kulübü\b', r'\bSpor Kulb\b', r'\bKulübü\b', r'\bKulb\b', r'\bS\.K\.\b', r'\bSK\b',
    r'\bA\.F\.C\.\b', r'\bAFC\b',
    r'\bU19\b', r'\bU21\b', r'\bU18\b', r'\bU17\b', r'\bU23\b', r'\bU20\b', r'\bU16\b',
    r'\bYL\b', r'\bAlt\.\b', r'\bRes\.\b', r'\bAcademy\b',
    r'\bFußball AG\b', r'\bFuball AG\b', r'\bAssociation\b', r'\bAthlitikos Omilos\b',
    r'\bKoninklijke Atletiek Associatie\b', r'\bOlympique Gymnaste Club\b',
    r'\bRacing Club de\b', r'\bSport Verein\b', r'\bCalcio\b', r'\bGirondins\b',
    r'\bOlympique de\b', r'\bOlympique\b', r'\bSporting Clube de\b', r'\bFutebol Clube do\b',
    r'\bSport Lisboa e\b',
]

# Populer kulupler icin elle belirlenmis kisa isimler. name LIKE pattern -> short_name.
# Regex temizliginden SONRA uygulanir, boylece her zaman kazanir.
ELITE_CLUB_OVERRIDES = [
    ("%Internazionale Milano%", "Inter"),
    ("%Associazione Calcio Milan%", "Milan"),
    ("%Real Madrid%", "Real Madrid"),
    ("%Barcelona%", "Barcelona"),
    ("Galatasaray%", "Galatasaray"),
    ("Fenerbah%", "Fenerbahçe"),
    ("Be%ikta%", "Beşiktaş"),
    ("Manchester United%", "Manchester United"),
    ("Manchester City%", "Manchester City"),
    ("Arsenal%", "Arsenal"),
    ("Chelsea%", "Chelsea"),
    ("Liverpool%", "Liverpool"),
    ("Juventus%", "Juventus"),
    ("%Bayern M%nchen%", "Bayern Munich"),
    ("Bayern Munich", "Bayern Munich"),
    ("%Paris Saint%Germain%", "PSG"),
    ("%Atl%tico%Madrid%", "Atlético Madrid"),
    ("Borussia Dortmund", "Borussia Dortmund"),
    ("Tottenham Hotspur%", "Tottenham Hotspur"),
    ("Societ% Sportiva Calcio Napoli", "Napoli"),
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
    ("PSV Eindhoven", "PSV"),
]


def clean_name(name):
    cleaned = name
    for pattern in SUFFIX_PATTERNS:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^[,\-\s]+|[,\-\s]+$', '', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'^Club\s+', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+Club$', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    return cleaned if cleaned else name


def run(batch_size=500):
    db = SessionLocal()
    try:
        teams = db.query(Team.id, Team.name, Team.short_name).all()
        print(f"{len(teams)} takim taraniyor...")

        updates = []
        for team_id, name, current_short in teams:
            new_short = clean_name(name)
            if new_short != current_short:
                updates.append({"id": team_id, "s": new_short})

        print(f"{len(updates)} takim guncellenecek. Elite override'lar uygulaniyor...")

        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            for row in batch:
                db.execute(text("UPDATE teams SET short_name = :s WHERE id = :id"), row)
            db.commit()
            print(f"  batch {i // batch_size + 1}/{(len(updates) - 1) // batch_size + 1} yazildi")

        override_count = 0
        for pattern, short_name in ELITE_CLUB_OVERRIDES:
            result = db.execute(
                text("UPDATE teams SET short_name = :s WHERE name LIKE :p"),
                {"s": short_name, "p": pattern},
            )
            override_count += result.rowcount or 0
        db.commit()
        print(f"{override_count} takim elite override ile guncellendi.")

        remaining_null = db.execute(
            text("SELECT COUNT(*) FROM teams WHERE short_name IS NULL")
        ).scalar()
        print(f"Bitti. short_name hala NULL olan takim sayisi: {remaining_null}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
