import requests
import json

def fetch_example():
    print("Fetching TMAPI data for Lionel Messi...")
    perf_resp = requests.get('https://tmapi.transfermarkt.technology/player/28003/performance-game', headers={'User-Agent': 'Mozilla/5.0'})
    perf_data = perf_resp.json()
    
    print("Fetching CEAPI data for Lionel Messi...")
    trans_resp = requests.get('https://www.transfermarkt.com.tr/ceapi/transferHistory/list/28003', headers={'User-Agent': 'Mozilla/5.0'})
    trans_data = trans_resp.json()
    
    example = {
        "ornek_oyuncu": "Lionel Messi (API ID: 28003)",
        "API_1_TMAPI_KULUP_VE_MILLI_MAC_ISTATISTIKLERI": [],
        "API_2_CEAPI_TRANSFER_GECMISI": []
    }
    
    # TMAPI'den 1 kulüp maçı, 1 milli maç alalım
    if 'data' in perf_data and 'performance' in perf_data['data']:
        matches = perf_data['data']['performance']
        if matches:
            # Sadece 2 maç örneği koyalım
            example["API_1_TMAPI_KULUP_VE_MILLI_MAC_ISTATISTIKLERI"] = matches[:2]
            
    # CEAPI'den 2 transfer alalım
    if 'transfers' in trans_data:
        example["API_2_CEAPI_TRANSFER_GECMISI"] = trans_data['transfers'][:2]
        
    with open('c:/Users/PC/Desktop/project/ornek_veri.json', 'w', encoding='utf-8') as f:
        json.dump(example, f, ensure_ascii=False, indent=4)
        
    print("Dosya başarıyla 'ornek_veri.json' olarak kaydedildi!")

if __name__ == '__main__':
    fetch_example()
