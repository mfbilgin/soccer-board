import requests
import time

API_KEY = "390515fce61c706a6dfcb807c93b81f6"

BASE_URL = "https://v3.football.api-sports.io"

HEADERS = {
    "x-apisports-key": API_KEY
}


def api_get(endpoint, **params):
    url = f"{BASE_URL}/{endpoint}"

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    time.sleep(1)

    return data