import sys
from pathlib import Path
import sqlite3

# Add project root to Python path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import DATABASE_PATH

SCHEMA_FILE = ROOT_DIR / "database" / "schema.sql"


def create_database():
    conn = sqlite3.connect(DATABASE_PATH)

    with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
        schema = file.read()

    conn.executescript(schema)

    conn.commit()
    conn.close()

    print("✅ Database and tables created successfully.")


if __name__ == "__main__":
    create_database()