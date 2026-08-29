"""
backfill_history.py

Optional helper for testing/demos: seeds N days of synthetic
historical data (both apix_daily and flight_fares) so the dashboard
immediately shows trends, YoY-style route movement, and alerts —
instead of waiting for the real scheduler to run for real days.

How it stays honest:
- Every synthetic day is anchored to your REAL base prices, read
  from apix_base_prices, then walked forward with a small random
  daily drift per route (a random walk), so the numbers look like
  plausible airfare movement instead of arbitrary noise.
- It only ever inserts PAST dates (yesterday and earlier). It never
  touches or overwrites today's real scraped data.
  get_current_route_prices() (in apix.py) always reads the single
  most recent scraped_at date in flight_fares, so as long as this
  script stays in the past, your real latest scrape remains the
  "current" price everywhere in the dashboard.
- APIx per synthetic day is computed with the exact same weighted
  formula as apix.py's calculate_apix(), just run locally against
  that day's synthetic prices instead of live DB current prices.

Prerequisite: run `python main.py` at least once first, so
apix_base_prices already has a row per route.

Usage:
    python backfill_history.py            # 30 days of history
    python backfill_history.py --days 60  # custom length
"""

import argparse
import random
from datetime import date, datetime, time, timedelta

import psycopg2

from config import DB_CONFIG, ROUTES, ROUTE_WEIGHTS


DAILY_DRIFT_PCT = 0.6          # max % a route's price can move, day to day
OFFERS_PER_ROUTE_PER_DAY = 6   # synthetic flight_fares rows per route/day


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def load_base_prices(cursor):
    cursor.execute("""
        SELECT origin, destination, base_price
        FROM apix_base_prices
    """)

    return {
        f"{origin}-{destination}": float(price)
        for origin, destination, price in cursor.fetchall()
    }


def calculate_apix(current_prices, base_prices):
    weighted_sum = 0
    total_weight = 0

    for route, weight in ROUTE_WEIGHTS.items():
        current = current_prices.get(route)
        base = base_prices.get(route)

        if current is None or not base:
            continue

        index = (current / base) * 100
        weighted_sum += index * weight
        total_weight += weight

    if total_weight == 0:
        return None

    return weighted_sum / total_weight


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="How many past days of history to generate (default 30)"
    )
    args = parser.parse_args()

    connection = get_connection()
    cursor = connection.cursor()

    base_prices = load_base_prices(cursor)

    if not base_prices:
        print(
            "No base prices found in apix_base_prices. "
            "Run `python main.py` at least once first."
        )
        cursor.close()
        connection.close()
        return

    print(f"Loaded base prices for {len(base_prices)} routes.")
    print(f"Generating {args.days} days of synthetic history...")
    print()

    # Walk forward from base price, day by day, ending at "yesterday"
    # (the oldest day is args.days ago, the newest synthetic day is
    # 1 day ago). Today itself is left untouched -- that's your real
    # scraped data.
    running_prices = dict(base_prices)
    today = date.today()

    for days_ago in range(args.days, 0, -1):
        day = today - timedelta(days=days_ago)

        for route in running_prices:
            drift_pct = random.uniform(-DAILY_DRIFT_PCT, DAILY_DRIFT_PCT)
            running_prices[route] *= (1 + drift_pct / 100)

        for origin, destination in ROUTES:
            route_key = f"{origin}-{destination}"
            price = running_prices.get(route_key)

            if price is None:
                continue

            for _ in range(OFFERS_PER_ROUTE_PER_DAY):
                offer_price = price * random.uniform(0.97, 1.03)

                scraped_at = datetime.combine(
                    day,
                    time(hour=random.randint(6, 21), minute=random.randint(0, 59))
                )

                cursor.execute("""
                    INSERT INTO flight_fares (
                        source, origin, destination, carrier, carrier_code,
                        flight_number, flight_date, scraped_at, advance_window,
                        fare_class, total_fare, currency, stops, status,
                        departure_time, arrival_time
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s
                    )
                """, (
                    "backfill", origin, destination, "Synthetic Air", "SA",
                    "SA000", day + timedelta(days=7), scraped_at, "T+7",
                    "Economy", round(offer_price, 2), "INR", 0, "AVAILABLE",
                    None, None
                ))

        apix_value = calculate_apix(running_prices, base_prices)

        if apix_value:
            cursor.execute("""
                INSERT INTO apix_daily (
                    index_date, frequency, apix_value, calculated_at
                ) VALUES (%s, 'Daily', %s, %s)
                ON CONFLICT (index_date, frequency) DO UPDATE
                SET
                    apix_value = EXCLUDED.apix_value,
                    calculated_at = EXCLUDED.calculated_at
            """, (
                day,
                round(apix_value, 2),
                datetime.combine(day, time(hour=23, minute=59))
            ))

            print(f"{day}:  APIx = {apix_value:.2f}")
        else:
            print(f"{day}:  skipped (no computable APIx)")

    connection.commit()
    cursor.close()
    connection.close()

    print()
    print("Backfill complete.")
    print(
        "Restart your API server (or it'll pick this up automatically "
        "on the next request) and refresh the dashboard."
    )


if __name__ == "__main__":
    main()
