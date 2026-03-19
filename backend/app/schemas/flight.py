from __future__ import annotations
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class FlightOut(BaseModel):
    id: UUID
    flight_number: str
    origin: str
    destination: str
    departure_at: datetime
    arrival_at: datetime
    available_seats: int

    model_config = {"from_attributes": True}