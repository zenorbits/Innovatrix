from datetime import date, datetime

from config import ROUTE_WEIGHTS

from database import (
    get_connection,
    save_apix
)


# ============================================================
# GET LATEST ROUTE PRICES
# ============================================================

def get_current_route_prices():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # Get latest collection date
        cursor.execute("""
            SELECT MAX(DATE(scraped_at))

            FROM flight_fares

            WHERE status = 'AVAILABLE'
        """)

        result = cursor.fetchone()

        if not result or result[0] is None:

            return {}

        latest_date = result[0]

        print(
            f"Current price date: {latest_date}"
        )

        # Get prices ONLY from latest day
        cursor.execute("""
            SELECT
                origin,
                destination,
                AVG(total_fare)

            FROM flight_fares

            WHERE
                status = 'AVAILABLE'
                AND DATE(scraped_at) = %s

            GROUP BY
                origin,
                destination
        """, (latest_date,))

        rows = cursor.fetchall()

        prices = {}

        for row in rows:

            route = (
                f"{row[0]}-{row[1]}"
            )

            prices[route] = float(row[2])

        return prices

    except Exception as e:

        print(
            "CURRENT PRICE ERROR:",
            e
        )

        return {}

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# GET BASE ROUTE PRICES
# ============================================================

def get_base_route_prices():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                origin,
                destination,
                base_price,
                base_date

            FROM apix_base_prices
        """)

        rows = cursor.fetchall()

        prices = {}

        base_date = None

        for row in rows:

            route = (
                f"{row[0]}-{row[1]}"
            )

            prices[route] = float(
                row[2]
            )

            base_date = row[3]

        if base_date:

            print(
                f"Base price date: {base_date}"
            )

        return prices

    except Exception as e:

        print(
            "BASE PRICE ERROR:",
            e
        )

        return {}

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ROUTE INDEX
# ============================================================

def calculate_route_index(
    current_price,
    base_price
):

    if base_price <= 0:

        return None

    return (
        current_price
        / base_price
    ) * 100


# ============================================================
# CALCULATE APIX
# ============================================================

def calculate_apix():

    current_prices = (
        get_current_route_prices()
    )

    base_prices = (
        get_base_route_prices()
    )

    if not current_prices:

        print(
            "No current prices available."
        )

        return 0

    if not base_prices:

        print(
            "No base prices available."
        )

        return 0

    weighted_sum = 0

    total_weight = 0

    print()

    print("=" * 70)

    print("ROUTE APIX")

    print("=" * 70)

    for route, weight in (
        ROUTE_WEIGHTS.items()
    ):

        current_price = (
            current_prices.get(route)
        )

        base_price = (
            base_prices.get(route)
        )

        if current_price is None:

            print(
                f"{route}: "
                f"No current data"
            )

            continue

        if base_price is None:

            print(
                f"{route}: "
                f"No base data"
            )

            continue

        route_index = (
            calculate_route_index(
                current_price,
                base_price
            )
        )

        if route_index is None:

            continue

        weighted_sum += (
            route_index * weight
        )

        total_weight += weight

        print(
            f"{route}: "
            f"Current ₹{current_price:.2f} | "
            f"Base ₹{base_price:.2f} | "
            f"Index {route_index:.2f} | "
            f"Weight {weight}"
        )

    if total_weight == 0:

        return 0

    apix = (
        weighted_sum
        / total_weight
    )

    return apix


# ============================================================
# DAILY APIX
# ============================================================

def calculate_daily_apix():

    return calculate_apix()


# ============================================================
# SAVE DAILY APIX
# ============================================================

def save_daily_apix():

    apix = calculate_daily_apix()

    if apix == 0:

        print(
            "APIx could not be calculated."
        )

        return 0

    save_apix(
        apix_value=apix,
        index_date=date.today(),
        frequency="Daily"
    )

    return apix


# ============================================================
# DISPLAY APIX
# ============================================================

def display_apix():

    apix = save_daily_apix()

    print()

    print("=" * 70)

    print(
        "REAL-TIME AIRFARE PRICE INDEX"
    )

    print("=" * 70)

    print(
        f"APIx: {apix:.2f}"
    )

    print(
        "Base Index: 100"
    )

    print(
        f"Calculated: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    print("=" * 70)
