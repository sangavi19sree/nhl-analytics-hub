import sys
from pathlib import Path
import sqlite3

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import DATABASE_PATH


def fetch_player_stats():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM players")
    total_players = cursor.fetchone()[0]

    print(f"Players available for processing: {total_players}")
    print("Player season stats implementation will be added in the next step.")

    conn.close()


if __name__ == "__main__":
    fetch_player_stats()