import json
from database import SessionLocal
from models import Team, PlayerStats, Player

LEAGUE_MAPPING = {
    'TR1': 'Süper Lig',
    'GB1': 'Premier League',
    'ES1': 'LaLiga',
    'IT1': 'Serie A',
    'FR1': 'Ligue 1',
    'L1': 'Bundesliga',
    'CL': 'UEFA Champions League',
    'CLQ': 'Champions League Qualifying',
    'EL': 'UEFA Europa League',
    'ELQ': 'Europa League Qualifying',
    'ECLQ': 'Europa Conference League Qual.',
    'FAC': 'FA Cup',
    'CGB': 'EFL Cup',
    'GBCS': 'Community Shield',
    'CDR': 'Copa del Rey',
    'CIT': 'Coppa Italia',
    'SCI': 'Supercoppa Italiana',
    'DFB': 'DFB-Pokal',
    'DFL': 'DFL-Supercup',
    'FRCH': 'Trophée des Champions',
    'NL1': 'Eredivisie',
    'NLP': 'KNVB Beker',
    'NLSC': 'Johan Cruijff Schaal',
    'PO1': 'Liga Portugal',
    'POCP': 'Taça de Portugal',
    'POSU': 'Supertaça Cândido de Oliveira',
    'RU1': 'Russian Premier League',
    'RUP': 'Russian Cup',
    'RUSS': 'Russian Super Cup',
    'UKR1': 'Ukrainian Premier League',
    'UKRP': 'Ukrainian Cup',
    'UKRS': 'Ukrainian Super Cup',
    'BE1': 'Jupiler Pro League',
    'BESC': 'Belgian Supercup',
    'GR1': 'Super League Greece',
    'GRP': 'Greek Cup',
    'SC1': 'Scottish Premiership',
    'SFA': 'Scottish FA Cup',
    'DK1': 'Superligaen',
    'DKP': 'Sydbank Pokalen',
    'KLUB': 'Club World Cup',
    'SUC': 'UEFA Super Cup',
    'AFCN': 'Africa Cup of Nations'
}

def export_data():
    db = SessionLocal()
    teams = [t.name for t in db.query(Team).all()]
    raw_leagues = [r[0] for r in db.query(PlayerStats.league_name).distinct().all()]
    nationalities = [r[0] for r in db.query(Player.nationality).filter(Player.nationality != None).distinct().all()]
    
    formatted_leagues = []
    for code in raw_leagues:
        name = LEAGUE_MAPPING.get(code, code)
        # Format: "Süper Lig (TR1)"
        formatted_leagues.append(f"{name} ({code})")
    
    data = {
        "teams": sorted(list(set(teams))),
        "leagues": sorted(list(set(formatted_leagues))),
        "nationalities": sorted(list(set(nationalities)))
    }
    
    with open("data-entry/db_data.js", "w", encoding="utf-8") as f:
        f.write(f"const DB_DATA = {json.dumps(data, ensure_ascii=False)};")
    
    print(f"Exported {len(data['teams'])} teams and {len(data['leagues'])} leagues.")

if __name__ == "__main__":
    export_data()
