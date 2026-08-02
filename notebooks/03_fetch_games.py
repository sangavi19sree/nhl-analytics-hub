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


def fetch_games():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT team_id, team_abbrev FROM teams")
    teams = cursor.fetchall()

    inserted = 0

    for team_id, team_abbrev in teams:

        print(f"Fetching {team_abbrev} schedule...")

        url = f"{BASE_URL}/club-schedule-season/{team_abbrev}/now"

        response = requests.get(url)

        if response.status_code != 200:
            continue

        data = response.json()

        games = data.get("games", [])

        for game in games:

            cursor.execute("""
                SELECT team_id FROM teams
                WHERE team_abbrev = ?
            """, (
                game.get("homeTeam", {}).get("abbrev"),
            ))

            home = cursor.fetchone()

            cursor.execute("""
                SELECT team_id FROM teams
                WHERE team_abbrev = ?
            """, (
                game.get("awayTeam", {}).get("abbrev"),
            ))

            away = cursor.fetchone()

            if not home or not away:
                continue

            cursor.execute("""
                INSERT OR IGNORE INTO games(
                    game_id,
                    season,
                    game_type,
                    game_date,
                    home_team_id,
                    away_team_id,
                    home_score,
                    away_score,
                    game_state,
                    venue_name
                )
                VALUES(?,?,?,?,?,?,?,?,?,?)
            """, (
                game.get("id"),
                game.get("season"),
                game.get("gameType"),
                game.get("gameDate"),
                home[0],
                away[0],
                game.get("homeTeam", {}).get("score"),
                game.get("awayTeam", {}).get("score"),
                game.get("gameState"),
                game.get("venue", {}).get("default")
            ))

            inserted += 1

        conn.commit()
        time.sleep(REQUEST_DELAY)

    conn.close()

    print(f"\nGames Processed : {inserted}")


if __name__ == "__main__":
    fetch_games()