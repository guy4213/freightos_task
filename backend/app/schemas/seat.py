from __future__ import annotations
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel
from app.models import SeatType


class SeatOut(BaseModel):
    id: UUID
    label: str
    row_number: int
    column_letter: str
    seat_type: SeatType
    base_price: Decimal
    status: str

    model_config = {"from_attributes": True}