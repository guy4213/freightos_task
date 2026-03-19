import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Date, Numeric, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class BookingStatus(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


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
    seat_id = Column(UUID(as_uuid=True), ForeignKey("seats.id"), nullable=False)
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