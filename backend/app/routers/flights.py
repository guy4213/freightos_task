from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import booking_service

router = APIRouter(prefix="/api/flights", tags=["flights"])


@router.get("")
def list_flights(db: Session = Depends(get_db)):
    return booking_service.get_flights(db)


@router.get("/{flight_id}/seats")
def get_seats(flight_id: UUID, db: Session = Depends(get_db)):
    return booking_service.get_flight_seats(db, flight_id)