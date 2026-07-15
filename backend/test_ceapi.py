import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

urls = [
    "https://www.transfermarkt.com.tr/ceapi/profile/player/28003",
    "https://www.transfermarkt.com.tr/ceapi/player/28003/performanceperclub",
    "https://www.transfermarkt.com.tr/ceapi/transferhistory/list/28003",
    "https://www.transfermarkt.com.tr/ceapi/player/28003/achievements",
    "https://www.transfermarkt.com.tr/ceapi/achievements/player/28003"
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"{url} -> {r.status_code}")
        if r.status_code == 200:
            print("  ", r.text[:150])
    except Exception as e:
        print(f"{url} -> Error: {e}")
