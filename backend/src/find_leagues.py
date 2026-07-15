import json

with open(
    "data/leagues/all_leagues.json",
    encoding="utf-8"
) as f:

    data = json.load(f)

while True:

    q = input(
        "\nLig ara (çıkmak için q): "
    ).strip()

    if q.lower() == "q":
        break

    for item in data["response"]:

        league_name = item["league"]["name"]

        if q.lower() in league_name.lower():

            print(
                f"{item['league']['id']:>4} | "
                f"{league_name:<30} | "
                f"{item['country']['name']}"
            )