"""
BookingService — all business logic lives here.
Routers call this service. Service calls repositories or DB directly.
"""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException
from sqlalchemy import func
from app.models import (
    Flight, Seat, Booking, BookingSeat, Passenger,
    BookingStatus
)
from app.schemas import BookingIn, BookingOut, BookingSeatOut, PassengerOut


def _calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _is_infant(dob: date) -> bool:
    return _calculate_age(dob) < 2


def _validate_infant_adult_ratio(seat_items: list):
    """Max 1 infant per adult (infants don't count as adults)."""
    infants = sum(1 for item in seat_items if _is_infant(item.passenger.date_of_birth))
    adults = len(seat_items) - infants

    if infants > adults:
        raise HTTPException(
            status_code=422,
            detail=f"Too many infants. You have {infants} infant(s) but only {adults} adult(s). "
                   f"Maximum 1 infant per adult."
        )


def _get_reserved_seat_ids_for_flight(db: Session, flight_id: UUID) -> set:
    """Return seat IDs that are already booked (active bookings only)."""
    rows = (
        db.query(BookingSeat.seat_id)
        .join(Booking, Booking.id == BookingSeat.booking_id)
        .filter(
            Booking.flight_id == flight_id,
            Booking.status == BookingStatus.active
        )
        .all()
    )
    return {row.seat_id for row in rows}


# ──────────────────────────────────────────────
# PUBLIC SERVICE FUNCTIONS
# ──────────────────────────────────────────────

def get_flights(db: Session) -> list:
    flights = db.query(Flight).order_by(Flight.departure_at).all()

    result = []
    for flight in flights:
        reserved_ids = _get_reserved_seat_ids_for_flight(db, flight.id)
        available_count = sum(1 for s in flight.seats if s.id not in reserved_ids)
        result.append({
            "id": flight.id,
            "flight_number": flight.flight_number,
            "origin": flight.origin,
            "destination": flight.destination,
            "departure_at": flight.departure_at,
            "arrival_at": flight.arrival_at,
            "available_seats": available_count,
        })
    return result


def get_flight_seats(db: Session, flight_id: UUID) -> list:
    flight = db.query(Flight).filter(Flight.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    reserved_ids = _get_reserved_seat_ids_for_flight(db, flight_id)

    seats_out = []
    for seat in sorted(flight.seats, key=lambda s: (s.row_number, s.column_letter)):
        seats_out.append({
            "id": seat.id,
            "label": f"{seat.row_number}{seat.column_letter}",
            "row_number": seat.row_number,
            "column_letter": seat.column_letter,
            "seat_type": seat.seat_type,
            "base_price": seat.base_price,
            "status": "reserved" if seat.id in reserved_ids else "available",
        })
    return seats_out


def _validate_no_duplicate_passenger_on_flight(db: Session, flight_id: UUID, seat_items: list):
    """Same person (name + DOB + phone) cannot appear twice on the same flight."""

    for item in seat_items:
        name = item.passenger.full_name.strip().lower()
        dob = item.passenger.date_of_birth
        phone = item.passenger.phone_number.strip()

        existing = (
            db.query(Passenger)
            .join(BookingSeat, BookingSeat.id == Passenger.booking_seat_id)
            .join(Booking, Booking.id == BookingSeat.booking_id)
            .filter(
                Booking.flight_id == flight_id,
                Booking.status == BookingStatus.active,
                func.lower(Passenger.full_name) == name,
                Passenger.date_of_birth == dob,
                Passenger.phone_number == phone,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=422,
                detail={
                    "type": "duplicate_passenger_on_flight",
                    "message": f'Passenger "{item.passenger.full_name}" is already booked on this flight (same name, date of birth, and phone number).'
                }
            )
def _validate_no_duplicate_passengers(seat_items: list):
    """No two passengers in the same booking can share name or phone."""
    names = []
    phones = []

    for item in seat_items:
        name = item.passenger.full_name.strip().lower()
        phone = item.passenger.phone_number.strip()

        if name in names:
            raise HTTPException(
                status_code=422,
                detail={
                    "type": "duplicate_name",
                    "message": f'Duplicate passenger name: "{item.passenger.full_name}". Each passenger must have a unique name.'
                }
            )
        if phone in phones:
            raise HTTPException(
                status_code=422,
                detail={
                    "type": "duplicate_phone",
                    "message": f'Duplicate phone number: "{item.passenger.phone_number}". Each passenger must have a unique phone number.'
                }
            )

        names.append(name)
        phones.append(phone)
def create_booking(db: Session, payload: BookingIn) -> BookingOut:
    # ── Step 1: Validate infant/adult ratio ──
    _validate_infant_adult_ratio(payload.seats)
    _validate_no_duplicate_passengers(payload.seats)
    _validate_no_duplicate_passenger_on_flight(db, payload.flight_id, payload.seats)

    # ── Step 2: Load seats from DB (never trust client prices) ──
    seat_ids = [item.seat_id for item in payload.seats]
    seats_in_db = db.query(Seat).filter(Seat.id.in_(seat_ids)).all()

    if len(seats_in_db) != len(seat_ids):
        raise HTTPException(status_code=404, detail="One or more seats not found")

    # Verify all seats belong to the requested flight
    for seat in seats_in_db:
        if seat.flight_id != payload.flight_id:
            raise HTTPException(
                status_code=422,
                detail=f"Seat {seat.label} does not belong to this flight"
            )

    # ── Step 3: Check availability (inside transaction with row lock) ──
    # Lock the seat rows to prevent concurrent bookings
    locked_seats = (
        db.query(Seat)
        .filter(Seat.id.in_(seat_ids))
        .with_for_update()
        .all()
    )

    reserved_ids = _get_reserved_seat_ids_for_flight(db, payload.flight_id)
    conflicts = [s for s in locked_seats if s.id in reserved_ids]

    if conflicts:
        conflict_labels = [f"{s.row_number}{s.column_letter}" for s in conflicts]
        raise HTTPException(
            status_code=409,
            detail=f"Seats already reserved: {', '.join(conflict_labels)}. Please go back and reselect."
        )

    # ── Step 4: Calculate total price from DB values (never from frontend) ──
    seat_price_map = {s.id: s.base_price for s in seats_in_db}
    total_price = sum(seat_price_map[sid] for sid in seat_ids)

    # ── Step 5: Insert everything atomically ──
    for item in payload.seats:
        dob = item.passenger.date_of_birth
        if dob >= date.today():
            raise HTTPException(
                status_code=422,
                detail="Date of birth must be in the past"
            )
        age = (date.today() - dob).days // 365
        if age > 120:
            raise HTTPException(
                status_code=422,
                detail="Age cannot exceed 120 years"
            )
    try:
        booking = Booking(
            session_id=payload.session_id,
            flight_id=payload.flight_id,
            booked_at=datetime.utcnow(),
            total_price=Decimal(str(total_price)),
            status=BookingStatus.active,
        )
        db.add(booking)
        db.flush()  # get booking.id

        for item in payload.seats:
            booking_seat = BookingSeat(
                booking_id=booking.id,
                seat_id=item.seat_id,
            )
            db.add(booking_seat)
            db.flush()  # get booking_seat.id

            dob = item.passenger.date_of_birth
            passenger = Passenger(
                booking_seat_id=booking_seat.id,
                full_name=item.passenger.full_name,
                date_of_birth=dob,
                phone_number=item.passenger.phone_number,
                is_infant=_is_infant(dob),
            )
            db.add(passenger)

        db.commit()
        db.refresh(booking)
    except HTTPException:
        db.rollback()
        raise  # ← זורק מחדש את ה-HTTPException המקורית בלי לשנות אותה
    except Exception as e:
        db.rollback()
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="One or more seats were just taken. Please go back and reselect."
            )
        raise HTTPException(status_code=500, detail="Booking failed. Please try again.")

    return _format_booking_out(db, booking)


def get_bookings_by_session(db: Session, session_id: UUID) -> list:
    bookings = (
        db.query(Booking)
        .filter(Booking.session_id == session_id)
        .order_by(Booking.booked_at.desc())
        .all()
    )
    return [_format_booking_out(db, b) for b in bookings]


def cancel_booking(db: Session, booking_id: UUID, session_id: UUID):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.session_id != session_id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(status_code=422, detail="Booking is already cancelled")

    booking.status = BookingStatus.cancelled
    db.commit()
    db.refresh(booking)

    return _format_booking_out(db, booking)

# ──────────────────────────────────────────────
# INTERNAL HELPER
# ──────────────────────────────────────────────

def _format_booking_out(db: Session, booking: Booking) -> dict:
    """Build the full response shape for a booking."""
    flight = db.query(Flight).filter(Flight.id == booking.flight_id).first()

    seats_out = []
    for bs in booking.booking_seats:
        seat = bs.seat
        passenger = bs.passenger
        seats_out.append({
            "id": bs.id,
            "seat_id": seat.id,
            "seat_label": f"{seat.row_number}{seat.column_letter}",
            "passenger": {
                "id": passenger.id,
                "full_name": passenger.full_name,
                "date_of_birth": passenger.date_of_birth,
                "phone_number": passenger.phone_number,
                "is_infant": passenger.is_infant,
            }
        })

    return {
        "id": booking.id,
        "session_id": booking.session_id,
        "flight_id": booking.flight_id,
        "flight_number": flight.flight_number,
        "origin": flight.origin,
        "destination": flight.destination,
        "departure_at": flight.departure_at,
        "booked_at": booking.booked_at,
        "total_price": booking.total_price,
        "status": booking.status,
        "seats": seats_out,
    }