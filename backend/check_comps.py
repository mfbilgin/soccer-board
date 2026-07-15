import requests
import json

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

resp = requests.get(f"{TMAPI_BASE}/player/29932/performance-game", headers=HEADERS)
if resp.status_code == 200:
    perf = resp.json()
    comps = set()
    for match in perf.get('data', {}).get('performance', []):
        comps.add(match.get('gameInformation', {}).get('competitionId'))
    print("Competitions returned:", comps)
else:
    print("Error:", resp.status_code)
