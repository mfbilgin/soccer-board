import requests
import json

url = "https://transfermarkt-api.vercel.app/players/29932/stats"
res = requests.get(url)
if res.status_code == 200:
    data = res.json()
    stats = data.get("stats", [])
    # filter for Bundesliga (L1)
    l1_stats = [s for s in stats if s.get("competitionID") == "L1"]
    print(json.dumps(l1_stats, indent=2))
else:
    print("API Error:", res.status_code)
