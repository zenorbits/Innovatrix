import time

from datetime import (
    date,
    timedelta
)

from threading import Thread

import uvicorn

from api import app

from apix import display_apix

from config import (
    ROUTES,
    WINDOWS,
    SCRAPE_DELAY,
    API_HOST,
    API_PORT,
    SCHEDULER_INTERVAL
)

from database import (
    create_tables,
    create_base_prices,
    save_flights
)

from flights import (
    collect_route,
    clean_data
)


# ============================================================
# COLLECT ALL DATA
# ============================================================

def collect_all_data():

    today = date.today()

    all_flights = []

    print()
    print("=" * 70)
    print("STARTING AIRFARE DATA COLLECTION")
    print("=" * 70)

    for origin, destination in ROUTES:

        for window, days in WINDOWS.items():

            flight_date = (
                today
                + timedelta(days=days)
            )

            flights = collect_route(
                origin,
                destination,
                flight_date,
                window
            )

            all_flights.extend(
                flights
            )

            time.sleep(
                SCRAPE_DELAY
            )

    print()
    print("=" * 70)
    print("DATA CLEANING")
    print("=" * 70)

    print(
        "Raw records:",
        len(all_flights)
    )

    cleaned = clean_data(
        all_flights
    )

    print(
        "Clean records:",
        len(cleaned)
    )

    save_flights(cleaned)

    return cleaned


# ============================================================
# DAILY SCHEDULER
# ============================================================

def daily_scheduler():

    while True:

        time.sleep(
            SCHEDULER_INTERVAL
        )

        try:

            print()
            print(
                "#" * 70
            )

            print(
                "DAILY UPDATE"
            )

            print(
                "#" * 70
            )

            collect_all_data()

            display_apix()

        except Exception as e:

            print(
                "SCHEDULER ERROR:",
                e
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "REAL-TIME AIRFARE PRICE INDEX"
    )
    print("=" * 70)

    # Database
    create_tables()

    # First data collection
    collect_all_data()

    # Create permanent base
    create_base_prices()

    # Calculate first APIx
    display_apix()

    # Start daily scheduler
    scheduler = Thread(
        target=daily_scheduler,
        daemon=True
    )

    scheduler.start()

    print()
    print("=" * 70)
    print("FASTAPI SERVER")
    print("=" * 70)

    print(
        f"API: "
        f"http://{API_HOST}:{API_PORT}"
    )

    print(
        f"Docs: "
        f"http://{API_HOST}:{API_PORT}/docs"
    )

    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT
    )
