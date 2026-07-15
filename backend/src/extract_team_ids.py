import json
from pathlib import Path

team_ids = []

for file in Path("data/teams").glob("*.json"):

    with open(
        file,
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    for item in data["response"]:

        team_ids.append(
            item["team"]["id"]
        )

team_ids = sorted(
    set(team_ids)
)

with open(
    "team_ids.json",
    "w"
) as f:

    json.dump(
        team_ids,
        f,
        indent=2
    )

print(
    len(team_ids),
    "team bulundu"
)