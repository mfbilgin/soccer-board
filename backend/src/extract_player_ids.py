import json
from pathlib import Path

player_ids = set()

for file in Path(
    "data/squads"
).glob("*.json"):

    with open(
        file,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    for squad in data["response"]:

        for player in squad["players"]:

            player_ids.add(
                player["id"]
            )

with open(
    "player_ids.json",
    "w"
) as f:

    json.dump(
        sorted(player_ids),
        f,
        indent=2
    )

print(
    len(player_ids),
    "oyuncu bulundu"
)