import uuid
import enum
from decimal import Decimal
from sqlalchemy import Column, String, Integer, Numeric, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class SeatType(str, enum.Enum):
    window = "window"
    middle = "middle"
    aisle = "aisle"


class Seat(Base):
    __tablename__ = "seats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_id = Column(UUID(as_uuid=True), ForeignKey("flights.id"), nullable=False)
    row_number = Column(Integer, nullable=False)
    column_letter = Column(String(1), nullable=False)
    seat_type = Column(Enum(SeatType), nullable=False)
    base_price = Column(Numeric(10, 2), nullable=False)

    flight = relationship("Flight", back_populates="seats")
    booking_seats = relationship("BookingSeat", back_populates="seat")

    __table_args__ = (
        UniqueConstraint("flight_id", "row_number", "column_letter", name="uq_seat_position"),
    )