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


def fetch_game_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT game_id FROM games")
    games = cursor.fetchall()

    total = 0

    for (game_id,) in games:

        print(f"Fetching Game {game_id}")

        url = f"{BASE_URL}/gamecenter/{game_id}/boxscore"

        response = requests.get(url)

        if response.status_code != 200:
            continue

        data = response.json()

        teams = data.get("playerByGameStats", {})

        for side in ["awayTeam", "homeTeam"]:

            team = teams.get(side, {})

            if side == "awayTeam":
                team_abbrev = data["awayTeam"]["abbrev"]
            else:
                team_abbrev = data["homeTeam"]["abbrev"]

            cursor.execute(
                "SELECT team_id FROM teams WHERE team_abbrev = ?",
                (team_abbrev,)
            )

            result = cursor.fetchone()

            if not result:
                continue

            team_id = result[0]

            forwards = team.get("forwards", [])
            defense = team.get("defense", [])

            for player in forwards + defense:

                cursor.execute("""
                    INSERT OR IGNORE INTO game_stats(
                        game_id,
                        player_id,
                        team_id,
                        goals,
                        assists,
                        points,
                        shots_on_goal,
                        penalty_min,
                        toi,
                        plus_minus
                    )
                    VALUES(?,?,?,?,?,?,?,?,?,?)
                """, (
                    game_id,
                    player.get("playerId"),
                    team_id,
                    player.get("goals"),
                    player.get("assists"),
                    player.get("points"),
                    player.get("sog"),
                    player.get("pim"),
                    player.get("toi"),
                    player.get("plusMinus")
                ))

                total += cursor.rowcount

        conn.commit()
        time.sleep(REQUEST_DELAY)

    conn.close()

    print(f"\nGame Stats Inserted : {total}")


if __name__ == "__main__":
    fetch_game_stats()