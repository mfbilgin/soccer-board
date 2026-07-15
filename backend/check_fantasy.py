import requests
import json

TMAPI_BASE = "https://tmapi.transfermarkt.technology"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def check_fantasy_assists():
    perf = requests.get(f"{TMAPI_BASE}/player/566723/performance-game", headers=HEADERS).json()
    if not perf or 'data' not in perf or 'performance' not in perf['data']:
        print("Could not fetch data")
        return
        
    fantasy_matches = []
    total_official = 0
    total_normal = 0
    
    for match in perf['data']['performance']:
        game_info = match.get('gameInformation', {})
        stats = match.get('statistics', {})
        gen_stats = stats.get('generalStatistics', {})
        event_stats = stats.get('goalStatistics', {}) or {}
        
        comp_id_api = game_info.get('competitionId')
        season_id = game_info.get('seasonId', '0')
        
        if comp_id_api == 'L1' and gen_stats.get('participationState') == 'played':
            # TM bazen assistsOfficial kullanir, bazen assists kullanir.
            # Eger ikisi de varsa farkli mi?
            assists_off = event_stats.get("assistsOfficial")
            assists_norm = event_stats.get("assists")
            
            a_off = int(assists_off) if assists_off is not None else 0
            a_norm = int(assists_norm) if assists_norm is not None else 0
            
            total_official += a_off
            total_normal += a_norm
            
            # Eger TMAPI assists (normal) degeri assistsOfficial'dan buyukse, fantezi asist vardir.
            # Veya tam tersi.
            if a_norm > a_off or a_off > a_norm:
                match_name = game_info.get('matchResult', 'Unknown Match')
                matchday = game_info.get('matchday', 'Unknown')
                fantasy_matches.append(f"Sezon {season_id}, Hafta {matchday} | official: {a_off}, normal: {a_norm} | {match_name}")
            
    print(f"Toplam Official Asist: {total_official}")
    print(f"Toplam Normal Asist: {total_normal}")
    print("\nFarkli Asist Verisi Olan Maclar (Fantezi Asistler):")
    for m in fantasy_matches:
        print(m)

if __name__ == "__main__":
    check_fantasy_assists()
