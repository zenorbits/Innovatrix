from datetime import date, datetime

import psycopg2
from fastapi import FastAPI

from config import DB_CONFIG
from apix import calculate_daily_apix


app = FastAPI(
    title="Real-Time Airfare Price Index API",
    version="1.0"
)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():

    return {
        "status": "running",
        "service":
            "Real-Time Airfare Price Index Backend",
        "timestamp":
            datetime.now().isoformat()
    }


# ============================================================
# DAILY APIX
# ============================================================

@app.get("/api/index/daily")
def daily_index():

    apix = calculate_daily_apix()

    return {
        "index_type": "Daily",
        "APIx": round(apix, 2),
        "base_index": 100,
        "calculated_at":
            datetime.now().isoformat()
    }


# ============================================================
# FARES
# ============================================================

@app.get("/api/fares")
def get_fares():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                source,
                origin,
                destination,
                carrier,
                carrier_code,
                flight_number,
                flight_date,
                scraped_at,
                advance_window,
                fare_class,
                total_fare,
                currency,
                stops,
                status,
                departure_time,
                arrival_time

            FROM flight_fares

            ORDER BY scraped_at DESC

            LIMIT 500
        """)

        rows = cursor.fetchall()

        columns = [
            "id",
            "source",
            "origin",
            "destination",
            "carrier",
            "carrier_code",
            "flight_number",
            "flight_date",
            "scraped_at",
            "advance_window",
            "fare_class",
            "total_fare",
            "currency",
            "stops",
            "status",
            "departure_time",
            "arrival_time"
        ]

        result = []

        for row in rows:

            record = dict(
                zip(columns, row)
            )

            for key, value in record.items():

                if isinstance(
                    value,
                    (date, datetime)
                ):

                    record[key] = (
                        value.isoformat()
                    )

            result.append(record)

        return {
            "count": len(result),
            "fares": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# ROUTE AVERAGES
# ============================================================

@app.get("/api/route-averages")
def route_averages():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                origin,
                destination,
                AVG(total_fare)

            FROM flight_fares

            WHERE status = 'AVAILABLE'

            GROUP BY
                origin,
                destination

            ORDER BY
                origin,
                destination
        """)

        rows = cursor.fetchall()

        result = {}

        for row in rows:

            route = (
                f"{row[0]}-{row[1]}"
            )

            result[route] = round(
                float(row[2]),
                2
            )

        return {
            "route_averages": result
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# APIX HISTORY
# ============================================================

@app.get("/api/index/history")
def apix_history():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                index_date,
                frequency,
                apix_value,
                calculated_at

            FROM apix_daily

            ORDER BY index_date ASC
        """)

        rows = cursor.fetchall()

        history = []

        for row in rows:

            history.append({
                "date":
                    row[0].isoformat(),

                "frequency":
                    row[1],

                "APIx":
                    float(row[2]),

                "calculated_at":
                    row[3].isoformat()
            })

        return {
            "count": len(history),
            "history": history
        }

    except Exception as e:

        return {
            "error": str(e)
        }

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
