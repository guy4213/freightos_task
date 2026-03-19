"""
Seed script: creates the DB tables and populates flights + seats.
Run with: python -m app.seed  (from /backend directory)
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.database import engine, SessionLocal, Base
from app.models import Flight, Seat, SeatType


# Seat type and price derived from column letter
COLUMN_CONFIG = {
    "A": (SeatType.window, Decimal("200.00")),
    "B": (SeatType.middle, Decimal("150.00")),
    "C": (SeatType.aisle,  Decimal("100.00")),
    "D": (SeatType.aisle,  Decimal("100.00")),
    "E": (SeatType.middle, Decimal("150.00")),
    "F": (SeatType.window, Decimal("200.00")),
}

FLIGHTS_DATA = [
    {
        "flight_number": "FR1001",
        "origin": "TLV",
        "destination": "LHR",
        "departure_at": datetime.utcnow() + timedelta(days=3),
        "arrival_at":   datetime.utcnow() + timedelta(days=3, hours=5),
    },
    {
        "flight_number": "FR1002",
        "origin": "TLV",
        "destination": "CDG",
        "departure_at": datetime.utcnow() + timedelta(days=5),
        "arrival_at":   datetime.utcnow() + timedelta(days=5, hours=4, minutes=30),
    },
    {
        "flight_number": "FR1003",
        "origin": "TLV",
        "destination": "JFK",
        "departure_at": datetime.utcnow() + timedelta(days=7),
        "arrival_at":   datetime.utcnow() + timedelta(days=7, hours=12),
    },
    {
        "flight_number": "FR1004",
        "origin": "TLV",
        "destination": "FCO",
        "departure_at": datetime.utcnow() + timedelta(days=10),
        "arrival_at":   datetime.utcnow() + timedelta(days=10, hours=3, minutes=45),
    },
]


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(Flight).count() > 0:
            print("Database already seeded. Skipping.")
            return

        print("Seeding flights and seats...")
        for flight_data in FLIGHTS_DATA:
            flight = Flight(**flight_data)
            db.add(flight)
            db.flush()  # get flight.id before committing

            # Create 60 seats: 10 rows × 6 columns
            for row in range(1, 11):
                for col in ["A", "B", "C", "D", "E", "F"]:
                    seat_type, base_price = COLUMN_CONFIG[col]
                    seat = Seat(
                        flight_id=flight.id,
                        row_number=row,
                        column_letter=col,
                        seat_type=seat_type,
                        base_price=base_price,
                    )
                    db.add(seat)

            print(f"  ✓ Flight {flight_data['flight_number']} + 60 seats created")

        db.commit()
        print("Seeding complete.")

    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()