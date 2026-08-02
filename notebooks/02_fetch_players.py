import sys
from pathlib import Path
import sqlite3
import requests
import time

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import DATABASE_PATH, BASE_URL, REQUEST_DELAY


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def fetch_players():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT team_id, team_abbrev FROM teams")
    teams = cursor.fetchall()

    total_players = 0

    for team_id, team_abbrev in teams:

        print(f"Fetching {team_abbrev} roster...")

        url = f"{BASE_URL}/roster/{team_abbrev}/current"

        response = requests.get(url)

        if response.status_code != 200:
            print(f"Failed: {team_abbrev}")
            continue

        data = response.json()

        positions = [
            ("forwards", "F"),
            ("defensemen", "D"),
            ("goalies", "G")
        ]

        for group, position in positions:

            players = data.get(group, [])

            for player in players:

                player_id = player.get("id")

                first_name = player.get("firstName", {}).get("default")
                last_name = player.get("lastName", {}).get("default")

                jersey = player.get("sweaterNumber")
                birth_date = player.get("birthDate")
                birth_country = player.get("birthCountry")

                height = player.get("heightInCentimeters")
                weight = player.get("weightInKilograms")

                shoots = player.get("shootsCatches")

                headshot = player.get("headshot")

                cursor.execute("""
                    INSERT OR IGNORE INTO players(
                        player_id,
                        team_id,
                        first_name,
                        last_name,
                        position,
                        jersey_number,
                        birth_date,
                        birth_country,
                        height_cm,
                        weight_kg,
                        shoots_catches,
                        headshot_url
                    )
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    player_id,
                    team_id,
                    first_name,
                    last_name,
                    position,
                    jersey,
                    birth_date,
                    birth_country,
                    height,
                    weight,
                    shoots,
                    headshot
                ))

                total_players += 1

        conn.commit()
        time.sleep(REQUEST_DELAY)

    conn.close()

    print(f"\nTotal Players Inserted : {total_players}")


if __name__ == "__main__":
    fetch_players()