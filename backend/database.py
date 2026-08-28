import psycopg2

from config import DB_CONFIG


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS flight_fares (

                id SERIAL PRIMARY KEY,

                source VARCHAR(100),

                origin VARCHAR(10) NOT NULL,

                destination VARCHAR(10) NOT NULL,

                carrier VARCHAR(100),

                carrier_code VARCHAR(10),

                flight_number VARCHAR(50),

                flight_date DATE,

                scraped_at TIMESTAMP,

                advance_window VARCHAR(10),

                fare_class VARCHAR(50),

                total_fare NUMERIC(10, 2),

                currency VARCHAR(10),

                stops INTEGER,

                status VARCHAR(30),

                departure_time TIMESTAMP,

                arrival_time TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apix_daily (

                id SERIAL PRIMARY KEY,

                index_date DATE NOT NULL,

                frequency VARCHAR(20) NOT NULL,

                apix_value NUMERIC(10, 2) NOT NULL,

                calculated_at TIMESTAMP NOT NULL,

                UNIQUE(index_date, frequency)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS apix_base_prices (

                id SERIAL PRIMARY KEY,

                origin VARCHAR(10) NOT NULL,

                destination VARCHAR(10) NOT NULL,

                base_price NUMERIC(10, 2) NOT NULL,

                base_date DATE NOT NULL,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(origin, destination)
            )
        """)

        connection.commit()

        print("Database tables ready.")

    except Exception as e:

        if connection:
            connection.rollback()

        print("DATABASE TABLE ERROR:")
        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# SAVE FLIGHTS
# ============================================================

def save_flights(flights):

    if not flights:

        print("No flight records to save.")

        return

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        for flight in flights:

            cursor.execute("""
                INSERT INTO flight_fares (

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

                )

                VALUES (

                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s

                )
            """, (

                flight.get("source"),
                flight.get("origin"),
                flight.get("destination"),
                flight.get("carrier"),
                flight.get("carrier_code"),
                flight.get("flight_number"),
                flight.get("flight_date"),
                flight.get("scraped_at"),
                flight.get("advance_window"),
                flight.get("fare_class"),
                flight.get("total_fare"),
                flight.get("currency"),
                flight.get("stops"),
                flight.get("status"),
                flight.get("departure_time"),
                flight.get("arrival_time")
            ))

        connection.commit()

        print(
            f"Saved {len(flights)} flight records."
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print("DATABASE SAVE ERROR:")
        print(e)

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# CREATE BASE PRICES
# ============================================================

def create_base_prices():

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # Check if base already exists
        cursor.execute("""
            SELECT COUNT(*)
            FROM apix_base_prices
        """)

        count = cursor.fetchone()[0]

        if count > 0:

            print("APIx base prices already exist.")

            return

        # Find first collection date
        cursor.execute("""
            SELECT MIN(DATE(scraped_at))

            FROM flight_fares

            WHERE status = 'AVAILABLE'
        """)

        result = cursor.fetchone()

        if not result or result[0] is None:

            print(
                "No flight data available "
                "for APIx base."
            )

            return

        base_date = result[0]

        # Calculate route averages
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
        """, (base_date,))

        rows = cursor.fetchall()

        for row in rows:

            origin = row[0]

            destination = row[1]

            base_price = float(row[2])

            cursor.execute("""
                INSERT INTO apix_base_prices (

                    origin,
                    destination,
                    base_price,
                    base_date

                )

                VALUES (
                    %s,
                    %s,
                    %s,
                    %s
                )

                ON CONFLICT (
                    origin,
                    destination
                )

                DO NOTHING
            """, (
                origin,
                destination,
                base_price,
                base_date
            ))

        connection.commit()

        print(
            f"APIx base prices created "
            f"from {base_date}."
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "BASE PRICE ERROR:",
            e
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# SAVE APIX
# ============================================================

def save_apix(
    apix_value,
    index_date,
    frequency
):

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO apix_daily (

                index_date,
                frequency,
                apix_value,
                calculated_at

            )

            VALUES (
                %s,
                %s,
                %s,
                CURRENT_TIMESTAMP
            )

            ON CONFLICT (
                index_date,
                frequency
            )

            DO UPDATE SET

                apix_value =
                    EXCLUDED.apix_value,

                calculated_at =
                    CURRENT_TIMESTAMP
        """, (
            index_date,
            frequency,
            apix_value
        ))

        connection.commit()

        print(
            f"APIx saved: "
            f"{index_date} | "
            f"{frequency} | "
            f"{apix_value:.2f}"
        )

    except Exception as e:

        if connection:
            connection.rollback()

        print(
            "APIX SAVE ERROR:",
            e
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()


# ============================================================
# APIX HISTORY
# ============================================================

def get_apix_history():

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

        return cursor.fetchall()

    except Exception as e:

        print(
            "APIX HISTORY ERROR:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()
