from pathlib import Path
import json

from api_client import api_get
from utils import save_json


ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"

LEAGUES_FILE = (
    DATA_DIR
    / "leagues"
    / "selected_leagues.json"
)

OUTPUT_DIR = (
    DATA_DIR
    / "players_by_league"
)

SEASON = 2024


def load_leagues():

    with open(
        LEAGUES_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def page_file(
    league_id: int,
    page: int
) -> Path:

    return (
        OUTPUT_DIR
        / str(league_id)
        / f"page_{page}.json"
    )


def fetch_page(
    league_id: int,
    page: int
):

    output_file = page_file(
        league_id,
        page
    )

    if output_file.exists():

        print(
            f"SKIP | League={league_id} Page={page}"
        )

        return None

    print(
        f"FETCH | League={league_id} Page={page}"
    )

    data = api_get(
        "players",
        league=league_id,
        season=SEASON,
        page=page
    )

    save_json(
        data,
        output_file
    )

    return data


def main():

    leagues = load_leagues()

    for league in leagues:

        league_id = (
            league["league"]["id"]
        )

        league_name = (
            league["league"]["name"]
        )

        print(
            "\n"
            + "=" * 50
        )

        print(
            f"{league_name} ({league_id})"
        )

        print(
            "=" * 50
        )

        #
        # İlk sayfa
        #
        first_page_file = page_file(
            league_id,
            1
        )

        if first_page_file.exists():

            print(
                "Page 1 mevcut."
            )

            with open(
                first_page_file,
                "r",
                encoding="utf-8"
            ) as f:

                first_page = json.load(f)

        else:

            first_page = fetch_page(
                league_id,
                1
            )

        total_pages = (
            first_page["paging"]["total"]
        )

        print(
            f"Toplam sayfa: "
            f"{total_pages}"
        )

        #
        # Tüm sayfalar
        #
        for page in range(
            2,
            total_pages + 1
        ):

            fetch_page(
                league_id,
                page
            )

    print(
        "\nTüm ligler tamamlandı."
    )


if __name__ == "__main__":
    main()