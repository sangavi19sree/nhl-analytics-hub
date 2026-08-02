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


def fetch_teams():

    url = f"{BASE_URL}/standings/now"

    print("Fetching Teams...")

    response = requests.get(url)

    if response.status_code != 200:
        print("API Error:", response.status_code)
        return

    data = response.json()

    standings = data.get("standings", [])

    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0

    for item in standings:

        team_abbrev = item.get("teamAbbrev", {}).get("default")
        team_name = item.get("teamName", {}).get("default")
        conference = item.get("conferenceName")
        division = item.get("divisionName")
        logo = item.get("teamLogo")

        cursor.execute("""
            INSERT OR IGNORE INTO teams
            (
                team_abbrev,
                team_name,
                conference_name,
                division_name,
                logo_url
            )
            VALUES (?, ?, ?, ?, ?)
        """,
        (
            team_abbrev,
            team_name,
            conference,
            division,
            logo
        ))

        inserted += 1

    conn.commit()
    conn.close()

    print(f"{inserted} teams inserted successfully.")

    time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    fetch_teams()