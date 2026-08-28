import statistics
from datetime import datetime

import requests

from config import (
    SERPAPI_API_KEY,
    SERPAPI_URL,
    CURRENCY,
    REQUEST_TIMEOUT
)


# ============================================================
# SEARCH FLIGHTS
# ============================================================

def search_flights(
    origin,
    destination,
    flight_date
):

    params = {
        "engine": "google_flights",
        "api_key": SERPAPI_API_KEY,
        "departure_id": origin,
        "arrival_id": destination,
        "outbound_date": str(flight_date),
        "type": "2",
        "gl": "in",
        "hl": "en",
        "currency": CURRENCY
    }

    try:

        response = requests.get(
            SERPAPI_URL,
            params=params,
            timeout=REQUEST_TIMEOUT
        )

        print(
            f"SerpApi status "
            f"{origin}-{destination}: "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            print(response.text)
            return {}

        data = response.json()

        if "error" in data:

            print(
                "SERPAPI ERROR:",
                data["error"]
            )

            return {}

        return data

    except requests.exceptions.RequestException as e:

        print("CONNECTION ERROR:", e)
        return {}

    except Exception as e:

        print("SEARCH ERROR:", e)
        return {}


# ============================================================
# DATETIME
# ============================================================

def convert_datetime(value):

    if not value:
        return None

    try:

        return datetime.strptime(
            value,
            "%Y-%m-%d %H:%M"
        )

    except Exception:

        return None


# ============================================================
# AIRLINE CODE
# ============================================================

def get_airline_code(airline):

    codes = {
        "IndiGo": "6E",
        "Air India": "AI",
        "Air India Express": "IX",
        "Akasa Air": "QP",
        "SpiceJet": "SG"
    }

    return codes.get(
        airline,
        ""
    )


# ============================================================
# TOTAL FARE
# ============================================================

def extract_fare(result):

    price = result.get("price")

    if price is None:
        return None

    try:

        price = float(price)

    except (TypeError, ValueError):

        return None

    if price <= 0:
        return None

    return price


# ============================================================
# EXTRACT FLIGHTS
# ============================================================

def extract_flights(
    data,
    origin,
    destination,
    flight_date,
    window
):

    flights = []

    results = []

    results.extend(
        data.get(
            "best_flights",
            []
        )
    )

    results.extend(
        data.get(
            "other_flights",
            []
        )
    )

    for result in results:

        try:

            total_fare = extract_fare(
                result
            )

            if total_fare is None:
                continue

            segments = result.get(
                "flights",
                []
            )

            if not segments:
                continue

            first = segments[0]
            last = segments[-1]

            airline = first.get(
                "airline",
                "Unknown"
            )

            flight_number = first.get(
                "flight_number",
                "N/A"
            )

            departure_airport = first.get(
                "departure_airport",
                {}
            )

            arrival_airport = last.get(
                "arrival_airport",
                {}
            )

            departure_time = (
                departure_airport.get("time")
            )

            arrival_time = (
                arrival_airport.get("time")
            )

            stops = max(
                len(segments) - 1,
                0
            )

            fare_class = first.get(
                "travel_class",
                "Economy"
            )

            flight = {

                "source":
                    "SerpApi-GoogleFlights",

                "origin":
                    origin,

                "destination":
                    destination,

                "carrier":
                    airline,

                "carrier_code":
                    get_airline_code(
                        airline
                    ),

                "flight_number":
                    flight_number,

                "flight_date":
                    flight_date,

                "scraped_at":
                    datetime.now(),

                "advance_window":
                    window,

                "fare_class":
                    fare_class,

                "total_fare":
                    total_fare,

                "currency":
                    CURRENCY,

                "stops":
                    stops,

                "status":
                    "AVAILABLE",

                "departure_time":
                    convert_datetime(
                        departure_time
                    ),

                "arrival_time":
                    convert_datetime(
                        arrival_time
                    ),

                "booking_token":
                    result.get(
                        "booking_token"
                    )
            }

            flights.append(flight)

        except Exception as e:

            print(
                "Flight extraction error:",
                e
            )

    return flights


# ============================================================
# DUPLICATES
# ============================================================

def remove_duplicates(flights):

    unique = {}

    for flight in flights:

        key = (
            flight.get("origin"),
            flight.get("destination"),
            flight.get("carrier"),
            flight.get("flight_number"),
            flight.get("flight_date"),
            flight.get("advance_window"),
            flight.get("total_fare")
        )

        unique[key] = flight

    return list(unique.values())


# ============================================================
# OUTLIERS
# ============================================================

def remove_outliers(flights):

    if len(flights) < 4:
        return flights

    prices = [
        float(f["total_fare"])
        for f in flights
        if f.get("total_fare") is not None
    ]

    if len(prices) < 4:
        return flights

    median = statistics.median(prices)

    cleaned = []

    for flight in flights:

        price = float(
            flight["total_fare"]
        )

        if price < median * 0.10:
            continue

        if price > median * 5:
            continue

        cleaned.append(flight)

    return cleaned


# ============================================================
# CLEAN DATA
# ============================================================

def clean_data(flights):

    if not flights:
        return []

    valid = []

    for flight in flights:

        price = flight.get(
            "total_fare"
        )

        if price is None:
            continue

        try:

            price = float(price)

        except (TypeError, ValueError):

            continue

        if price <= 0:
            continue

        valid.append(flight)

    valid = remove_outliers(valid)

    valid = remove_duplicates(valid)

    return valid


# ============================================================
# COLLECT ROUTE
# ============================================================

def collect_route(
    origin,
    destination,
    flight_date,
    window
):

    print()
    print(
        f"Searching "
        f"{origin} -> {destination}"
    )

    print(
        f"Advance window: {window}"
    )

    print(
        f"Flight date: {flight_date}"
    )

    data = search_flights(
        origin,
        destination,
        flight_date
    )

    if not data:

        return []

    flights = extract_flights(
        data,
        origin,
        destination,
        flight_date,
        window
    )

    print(
        f"Offers received: "
        f"{len(flights)}"
    )

    return flights
