from datetime import date, datetime

import psycopg2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import DB_CONFIG, ROUTES
from apix import (
    calculate_daily_apix,
    get_current_route_prices,
    get_base_route_prices
)


app = FastAPI(
    title="Real-Time Airfare Price Index API",
    version="1.0"
)

# ============================================================
# CORS
# ============================================================
# The React dashboard (Vite dev server on :5173, or a static
# production build) needs to be able to call this API directly.
# The Vite dev proxy already handles same-origin /api/* calls in
# dev, but CORS is required for a production build or for anyone
# hitting the API from a different host/port.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# CITY METADATA (for the heatmap / route naming)
# ============================================================

CITY_INFO = {
    "DEL": {"id": "delhi", "name": "Delhi", "x": 150, "y": 55},
    "BOM": {"id": "mumbai", "name": "Mumbai", "x": 50, "y": 228},
    "BLR": {"id": "bengaluru", "name": "Bengaluru", "x": 150, "y": 285},
    "CCU": {"id": "kolkata", "name": "Kolkata", "x": 250, "y": 112},
    "HYD": {"id": "hyderabad", "name": "Hyderabad", "x": 50, "y": 112},
    "MAA": {"id": "chennai", "name": "Chennai", "x": 250, "y": 228}
}


def route_pct_change(origin, destination, current_prices, base_prices):
    """% change of a route's latest average fare vs its recorded base fare."""

    route_key = f"{origin}-{destination}"

    current = current_prices.get(route_key)
    base = base_prices.get(route_key)

    if current is None or not base:
        return None

    return ((current - base) / base) * 100


def tier_for_pct(pct):
    """Matches the thresholds shown in the frontend heatmap legend."""

    if pct is None:
        return "low"

    if pct > 15:
        return "high"

    if pct >= 5:
        return "medium"

    return "low"


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


# ============================================================
# DASHBOARD: KPIs
# ============================================================
# Matches the shape the frontend's dashboardService.getKpis() expects.

@app.get("/api/kpis")
def get_kpis():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        apix_now = calculate_daily_apix()

        cursor.execute("""
            SELECT index_date, apix_value

            FROM apix_daily

            WHERE frequency = 'Daily'

            ORDER BY index_date DESC
        """)

        rows = cursor.fetchall()

        month_ago_value = None
        week_ago_value = None

        if rows:

            latest_date = rows[0][0]

            for index_date, apix_value in rows:

                days_diff = (latest_date - index_date).days

                if week_ago_value is None and days_diff >= 7:
                    week_ago_value = float(apix_value)

                if month_ago_value is None and days_diff >= 30:
                    month_ago_value = float(apix_value)

        def pct_change(current, previous):

            if not previous:
                return 0

            return round(
                ((current - previous) / previous) * 100,
                2
            )

        monthly_change = pct_change(apix_now, month_ago_value)
        weekly_change = pct_change(apix_now, week_ago_value)

        if abs(monthly_change) > 15 or abs(weekly_change) > 5:
            alert_level = "HIGH"
        elif abs(monthly_change) > 5 or abs(weekly_change) > 2:
            alert_level = "MEDIUM"
        else:
            alert_level = "LOW"

        cursor.execute("""
            SELECT COUNT(DISTINCT origin || '-' || destination)

            FROM flight_fares
        """)

        row = cursor.fetchone()

        routes_count = row[0] if row and row[0] else len(ROUTES)

        return {
            "airfareApix": {
                "value": round(apix_now, 2),
                "changePct": monthly_change,
                "changeLabel": "vs last month"
            },
            "weeklyInflationChange": {
                "changePct": weekly_change,
                "changeLabel": "vs last week"
            },
            "routesMonitored": {
                "value": routes_count,
                "label": "Major city pairs"
            },
            "alertLevel": {
                "level": alert_level
            }
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
# DASHBOARD: TREND
# ============================================================
# Matches getTrend(). Only APIx is plotted since the pipeline
# doesn't collect an external CPI series to compare against.

@app.get("/api/trend")
def get_trend(range: str = "5y"):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT index_date, apix_value

            FROM apix_daily

            WHERE frequency = 'Daily'

            ORDER BY index_date ASC
        """)

        rows = cursor.fetchall()

        labels = [row[0].isoformat() for row in rows]
        data = [float(row[1]) for row in rows]

        return {
            "labels": labels,
            "series": [
                {
                    "key": "apix",
                    "name": "APIx",
                    "data": data
                }
            ]
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
# DASHBOARD: ROUTE HEATMAP
# ============================================================
# Matches getHeatmap(). Tiers follow the same thresholds shown
# in the frontend legend (>15% high, 5-15% medium, <5% low).

@app.get("/api/routes/heatmap")
def routes_heatmap():

    current_prices = get_current_route_prices()
    base_prices = get_base_route_prices()

    cities_used = set()
    routes = []

    for origin, destination in ROUTES:

        if origin not in CITY_INFO or destination not in CITY_INFO:
            continue

        pct = route_pct_change(
            origin,
            destination,
            current_prices,
            base_prices
        )

        cities_used.add(origin)
        cities_used.add(destination)

        routes.append({
            "from": CITY_INFO[origin]["id"],
            "to": CITY_INFO[destination]["id"],
            "tier": tier_for_pct(pct)
        })

    cities = [
        {
            "id": info["id"],
            "name": info["name"],
            "x": info["x"],
            "y": info["y"]
        }
        for code, info in CITY_INFO.items()
        if code in cities_used
    ]

    return {
        "cities": cities,
        "routes": routes
    }


# ============================================================
# DASHBOARD: TOP ROUTES
# ============================================================
# Matches getTopRoutes(). "yoyPct" here is the % change of a
# route's latest average fare vs its recorded base fare (the
# pipeline doesn't yet retain a full year of history to compute
# a true year-over-year figure).

@app.get("/api/routes/top")
def routes_top(limit: int = 5):

    current_prices = get_current_route_prices()
    base_prices = get_base_route_prices()

    results = []

    for origin, destination in ROUTES:

        pct = route_pct_change(
            origin,
            destination,
            current_prices,
            base_prices
        )

        if pct is None:
            continue

        origin_name = CITY_INFO.get(origin, {}).get("name", origin)
        destination_name = CITY_INFO.get(destination, {}).get("name", destination)

        results.append({
            "route": f"{origin_name} \u2192 {destination_name}",
            "yoyPct": round(pct, 2),
            "tier": tier_for_pct(pct)
        })

    results.sort(
        key=lambda item: item["yoyPct"],
        reverse=True
    )

    return results[:limit]


# ============================================================
# DASHBOARD: ALERTS
# ============================================================
# Matches getAlerts(). Generated on the fly from route price
# movements since the pipeline doesn't yet persist an alerts
# table.

@app.get("/api/alerts")
def get_alerts(limit: int = 10):

    current_prices = get_current_route_prices()
    base_prices = get_base_route_prices()

    alerts = []
    next_id = 1

    for origin, destination in ROUTES:

        pct = route_pct_change(
            origin,
            destination,
            current_prices,
            base_prices
        )

        if pct is None or abs(pct) < 5:
            continue

        origin_name = CITY_INFO.get(origin, {}).get("name", origin)
        destination_name = CITY_INFO.get(destination, {}).get("name", destination)
        direction = "up" if pct > 0 else "down"

        alerts.append({
            "id": next_id,
            "tier": tier_for_pct(pct),
            "message": (
                f"{origin_name}\u2013{destination_name} fares "
                f"{direction} {abs(pct):.1f}% vs base"
            ),
            "time": "Just now"
        })

        next_id += 1

    tier_order = {"high": 0, "medium": 1, "low": 2}

    alerts.sort(key=lambda item: tier_order[item["tier"]])

    return alerts[:limit]
