import requests
import json

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def prove_assists():
    perf = requests.get(f"{TMAPI_BASE}/player/566723/performance-game", headers=HEADERS).json()
    if not perf or 'data' not in perf or 'performance' not in perf['data']:
        print("Could not fetch data")
        return
        
    l1_matches = []
    total_assists_scraper = 0
    
    for match in perf['data']['performance']:
        game_info = match.get('gameInformation', {})
        stats = match.get('statistics', {})
        gen_stats = stats.get('generalStatistics', {})
        event_stats = stats.get('goalStatistics', {}) or {}
        
        comp_id_api = game_info.get('competitionId')
        season_id = game_info.get('seasonId', '0')
        
        if comp_id_api == 'L1' and gen_stats.get('participationState') == 'played':
            def _get_val(d, keys):
                for k in keys:
                    if d.get(k) is not None:
                        return d.get(k)
                return 0
            
            assists_official = _get_val(event_stats, ["assistsOfficial"])
            assists_normal = _get_val(event_stats, ["assists"])
            
            assists_used = int(assists_official if assists_official is not None else (assists_normal or 0))
            total_assists_scraper += assists_used
            
            if assists_used > 0:
                l1_matches.append(f"Sezon: {season_id}, Hafta: {game_info.get('matchday')} -> Asist: {assists_used}")
            
    print(f"JSON'dan Cikan Toplam Asist: {total_assists_scraper}")
    print("\nAsist Yapilan Maclarin Dokumu:")
    for m in l1_matches:
        print(m)

if __name__ == "__main__":
    prove_assists()
