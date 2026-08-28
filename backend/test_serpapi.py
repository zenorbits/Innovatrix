import json

from datetime import (
    date,
    timedelta
)

from config import ROUTES

from flights import (
    search_flights
)


# ============================================================
# TEST SERPAPI
# ============================================================

def main():

    origin, destination = ROUTES[0]

    flight_date = (
        date.today()
        + timedelta(days=7)
    )

    print("=" * 70)

    print(
        "SERPAPI TEST"
    )

    print("=" * 70)

    print(
        f"Route: "
        f"{origin} -> "
        f"{destination}"
    )

    print(
        f"Date: "
        f"{flight_date}"
    )

    print()

    print(
        "Sending request..."
    )

    data = search_flights(

        origin,

        destination,

        flight_date
    )

    if not data:

        print()

        print(
            "❌ No response received."
        )

        return

    print()

    print(
        "✅ Response received."
    )

    # --------------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------------

    filename = (
        "serpapi_response.json"
    )

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(

            data,

            file,

            indent=4,

            ensure_ascii=False
        )

    print()

    print(
        f"Full response saved to: "
        f"{filename}"
    )

    # --------------------------------------------------------
    # RESPONSE KEYS
    # --------------------------------------------------------

    print()

    print("=" * 70)

    print(
        "TOP-LEVEL RESPONSE KEYS"
    )

    print("=" * 70)

    for key in data.keys():

        print(
            " -",
            key
        )

    # --------------------------------------------------------
    # BEST FLIGHTS
    # --------------------------------------------------------

    best_flights = data.get(
        "best_flights",
        []
    )

    print()

    print("=" * 70)

    print(
        "BEST FLIGHTS"
    )

    print("=" * 70)

    print(
        "Number:",
        len(best_flights)
    )

    # --------------------------------------------------------
    # FIRST FLIGHT
    # --------------------------------------------------------

    if best_flights:

        first = best_flights[0]

        print()

        print(
            "Price:",
            first.get("price")
        )

        print(
            "Booking token:",
            "Available"
            if first.get(
                "booking_token"
            )
            else "Not available"
        )

        segments = first.get(
            "flights",
            []
        )

        for number, segment in enumerate(
            segments,
            start=1
        ):

            print()

            print(
                f"Segment {number}"
            )

            print(
                "  Airline:",
                segment.get(
                    "airline"
                )
            )

            print(
                "  Flight:",
                segment.get(
                    "flight_number"
                )
            )

            print(
                "  Aircraft:",
                segment.get(
                    "airplane"
                )
            )

            print(
                "  Class:",
                segment.get(
                    "travel_class"
                )
            )

    print()

    print("=" * 70)

    print(
        "TEST COMPLETE"
    )

    print("=" * 70)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()
