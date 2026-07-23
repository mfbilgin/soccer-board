"""
Takim isimlerini (teams.short_name) temizler.

- short_name'i hala NULL olan takimlarda, genel kurumsal ekleri (S.A.D., F.C.,
  A.S., Spor Kulubu, U19 vb.) regex ile silip sonucu short_name'e yazar.
- short_name zaten doluysa DOKUNMAZ: gercek kaynagi backend/scripts/
  backfill_team_profiles.py (TMAPI'nin kendi resmi short_name'i) ya da scraper'in
  kendisidir; bu script yalnizca o kaynaklarin kacirdigi satirlar icin bir
  yedek/fallback'tir. Eskiden burada bulunan ELITE_CLUB_OVERRIDES (LIKE '%X%'
  ile eslesen ~30 kulup listesi) kaldirildi, cunku alakasiz/farkli ulkelerden
  ayni alt-stringi paylasan kulupleri de ayni short_name'e cevirip birbirinden
  ayirt edilemez hale getiriyordu (orn. "Arsenal Tula" -> "Arsenal").
- Idempotent'tir: sadece short_name IS NULL olan satirlari isler ve degisen
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
        # Yalnizca short_name'i hala bos olan takimlari isle - zaten dolu olanlar
        # (TMAPI backfill'inden veya scraper'dan gelen) asla ezilmez.
        teams = db.query(Team.id, Team.name).filter(Team.short_name.is_(None)).all()
        print(f"{len(teams)} takim taraniyor (short_name IS NULL)...")

        updates = [{"id": team_id, "s": clean_name(name)} for team_id, name in teams]

        for i in range(0, len(updates), batch_size):
            batch = updates[i:i + batch_size]
            for row in batch:
                db.execute(text("UPDATE teams SET short_name = :s WHERE id = :id"), row)
            db.commit()
            print(f"  batch {i // batch_size + 1}/{(len(updates) - 1) // batch_size + 1} yazildi")

        remaining_null = db.execute(
            text("SELECT COUNT(*) FROM teams WHERE short_name IS NULL")
        ).scalar()
        print(f"Bitti. short_name hala NULL olan takim sayisi: {remaining_null}")
    finally:
        db.close()


if __name__ == "__main__":
    run()
