from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_session_id
from app.schemas import BookingIn
from app.services import booking_service

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("")
def create_booking(
    payload: BookingIn,
    session_id: UUID = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return booking_service.create_booking(db, payload, session_id)


@router.get("")
def list_bookings(
    session_id: UUID = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return booking_service.get_bookings_by_session(db, session_id)


@router.patch("/{booking_id}/cancel")
def cancel_booking(
    booking_id: UUID,
    session_id: UUID = Depends(get_session_id),
    db: Session = Depends(get_db)
):
    return booking_service.cancel_booking(db, booking_id, session_id)