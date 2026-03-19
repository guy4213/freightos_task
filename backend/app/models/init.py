import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean,
    ForeignKey, DateTime, Date, Enum, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class SeatType(str, enum.Enum):
    window = "window"
    middle = "middle"
    aisle = "aisle"


class BookingStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


class Flight(Base):
    __tablename__ = "flights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_number = Column(String, nullable=False, unique=True)
    origin = Column(String(3), nullable=False)       # IATA code e.g. "TLV"
    destination = Column(String(3), nullable=False)  # IATA code e.g. "LHR"
    departure_at = Column(DateTime, nullable=False)
    arrival_at = Column(DateTime, nullable=False)

    seats = relationship("Seat", back_populates="flight")
    bookings = relationship("Booking", back_populates="flight")


class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_id = Column(UUID(as_uuid=True), ForeignKey("flights.id"), nullable=False)
    row_number = Column(Integer, nullable=False)       # 1–10
    column_letter = Column(String(1), nullable=False)  # A–F
    seat_type = Column(Enum(SeatType), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)

    flight = relationship("Flight", back_populates="seats")
    booking_seats = relationship("BookingSeat", back_populates="seat")

    __table_args__ = (
        UniqueConstraint("flight_id", "row_number", "column_letter", name="uq_seat_position"),
    )

    @property
    def label(self):
        return f"{self.row_number}{self.column_letter}"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    flight_id = Column(UUID(as_uuid=True), ForeignKey("flights.id"), nullable=False)
    booked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.active, nullable=False)

    flight = relationship("Flight", back_populates="bookings")
    booking_seats = relationship("BookingSeat", back_populates="booking", cascade="all, delete-orphan")


class BookingSeat(Base):
    __tablename__ = "booking_seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False, unique=True)
    # unique=True on seat_id is the DB-level double-booking guard

    booking = relationship("Booking", back_populates="booking_seats")
    seat = relationship("Seat", back_populates="booking_seats")
    passenger = relationship("Passenger", back_populates="booking_seat", uselist=False, cascade="all, delete-orphan")


class Passenger(Base):
    __tablename__ = "passengers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_seat_id = Column(UUID(as_uuid=True), ForeignKey("booking_seats.id"), nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    phone_number = Column(String, nullable=False)
    is_infant = Column(Boolean, nullable=False, default=False)

    booking_seat = relationship("BookingSeat", back_populates="passenger")