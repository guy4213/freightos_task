import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Flight(Base):
    __tablename__ = "flights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_number = Column(String, nullable=False, unique=True)
    origin = Column(String(3), nullable=False)
    destination = Column(String(3), nullable=False)
    departure_at = Column(DateTime, nullable=False)
    arrival_at = Column(DateTime, nullable=False)

    seats = relationship("Seat", back_populates="flight")
    bookings = relationship("Booking", back_populates="flight")