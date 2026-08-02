import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.path.join(BASE_DIR, "database", "nhl.db")

DATA_PATH = os.path.join(BASE_DIR, "data")

BASE_URL = "https://api-web.nhle.com/v1"

REQUEST_DELAY = 0.5