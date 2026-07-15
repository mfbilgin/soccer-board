from pathlib import Path
import json


ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT
    / "data"
    / "leagues"
    / "all_leagues.json"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "leagues"
    / "selected_leagues.json"
)


TARGET_LEAGUE_IDS = {
    39, # İngiltere 1
    40, # İngiltere 2
    140, # İspanya 1
    141, # İspanya 2
    71, # İtalya 1
    72, # İtalya 2
    78, # Almanya 1
    79, # Almanya 2
    61, # Fransa 1
    62, # Fransa 2
    203, # Türkiye 1
    204, # Türkiye 2
    307, # SA 1
    253, # USA 1
    128, # Arjantin 1
    94, # Portekiz 1
    88, # Hollanda 1
    144, # Belçika 1
    207, # İsviçre 1
    218 # Avusturya 1
}


def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    selected = []

    for item in data["response"]:

        league_id = item["league"]["id"]

        if league_id in TARGET_LEAGUE_IDS:

            selected.append(item)

    selected.sort(
        key=lambda x: x["league"]["id"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            selected,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"{len(selected)} lig kaydedildi.\n"
    )

    print("Seçilen ligler:")

    for league in selected:

        print(
            f"{league['league']['id']} | "
            f"{league['league']['name']} | "
            f"{league['country']['name']}"
        )


if __name__ == "__main__":
    main()