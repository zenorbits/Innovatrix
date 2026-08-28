import os
from pathlib import Path

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# ============================================================
# SERPAPI
# ============================================================

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

SERPAPI_URL = "https://serpapi.com/search.json"


# ============================================================
# POSTGRESQL
# ============================================================

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "Sih"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}


# ============================================================
# ROUTES
# ============================================================

ROUTES = [
    ("DEL", "BOM"),
    ("DEL", "BLR"),
    ("BOM", "BLR"),
    ("DEL", "CCU"),
    ("BLR", "HYD"),
    ("MAA", "DEL")
]


# ============================================================
# ADVANCE PURCHASE WINDOWS
# ============================================================

WINDOWS = {
    "T+1": 1,
    "T+7": 7,
    "T+15": 15,
    "T+30": 30,
    "T+45": 45
}


# ============================================================
# ROUTE WEIGHTS
# ============================================================

ROUTE_WEIGHTS = {
    "DEL-BOM": 0.25,
    "DEL-BLR": 0.25,
    "BOM-BLR": 0.15,
    "DEL-CCU": 0.15,
    "BLR-HYD": 0.10,
    "MAA-DEL": 0.10
}


# ============================================================
# APPLICATION SETTINGS
# ============================================================

CURRENCY = "INR"

API_HOST = "127.0.0.1"

API_PORT = 8000

SCRAPE_DELAY = 2

REQUEST_TIMEOUT = 90

SCHEDULER_INTERVAL = 86400
