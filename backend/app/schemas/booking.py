from __future__ import annotations
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from typing import List
from pydantic import BaseModel, field_validator
from app.models import BookingStatus


class PassengerIn(BaseModel):
    full_name: str
    date_of_birth: date
    phone_number: str

    @field_validator("full_name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name cannot be empty")
        return v.strip()

    @field_validator("date_of_birth")
    @classmethod
    def dob_not_future(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("Date of birth must be in the past")
        return v

    @field_validator("phone_number")
    @classmethod
    def phone_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Phone number cannot be empty")
        return v.strip()


class PassengerOut(BaseModel):
    id: UUID
    full_name: str
    date_of_birth: date
    phone_number: str
    is_infant: bool

    model_config = {"from_attributes": True}


class SeatBookingIn(BaseModel):
    seat_id: UUID
    passenger: PassengerIn


class BookingIn(BaseModel):
    flight_id: UUID
    seats: List[SeatBookingIn]

    @field_validator("seats")
    @classmethod
    def validate_seat_count(cls, v: list) -> list:
        if len(v) == 0:
            raise ValueError("Must select at least one seat")
        if len(v) > 9:
            raise ValueError("Cannot book more than 9 seats per reservation")
        return v


class BookingSeatOut(BaseModel):
    id: UUID
    seat_id: UUID
    seat_label: str
    passenger: PassengerOut

    model_config = {"from_attributes": True}


class BookingOut(BaseModel):
    id: UUID
    flight_id: UUID
    flight_number: str
    origin: str
    destination: str
    departure_at: datetime
    booked_at: datetime
    total_price: Decimal
    status: BookingStatus
    seats: List[BookingSeatOut]

    model_config = {"from_attributes": True}