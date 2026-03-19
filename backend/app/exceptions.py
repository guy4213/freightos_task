from fastapi import HTTPException


class AppError(HTTPException):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(
            status_code=status_code,
            detail={
                "code": code,
                "message": message
            }
        )


# ── Predefined errors ──────────────────────────────────────
class SeatTakenError(AppError):
    def __init__(self, labels: str = ""):
        super().__init__(
            code="SEAT_TAKEN",
            message=f"Seats already reserved: {labels}. Please go back and reselect.",
            status_code=409
        )

class DuplicatePassengerNameError(AppError):
    def __init__(self, name: str):
        super().__init__(
            code="DUPLICATE_NAME",
            message=f'Duplicate passenger name: "{name}". Each passenger must have a unique name.',
            status_code=422
        )

class DuplicatePassengerPhoneError(AppError):
    def __init__(self, phone: str):
        super().__init__(
            code="DUPLICATE_PHONE",
            message=f'Duplicate phone number: "{phone}". Each passenger must have a unique phone number.',
            status_code=422
        )

class PassengerAlreadyOnFlightError(AppError):
    def __init__(self, name: str):
        super().__init__(
            code="PASSENGER_ALREADY_ON_FLIGHT",
            message=f'Passenger "{name}" is already booked on this flight.',
            status_code=422
        )

class TooManyInfantsError(AppError):
    def __init__(self, infants: int, adults: int):
        super().__init__(
            code="TOO_MANY_INFANTS",
            message=f"Too many infants ({infants}). You have {adults} adult(s). Maximum 1 infant per adult.",
            status_code=422
        )

class BookingNotFoundError(AppError):
    def __init__(self):
        super().__init__(
            code="BOOKING_NOT_FOUND",
            message="Booking not found.",
            status_code=404
        )

class UnauthorizedCancelError(AppError):
    def __init__(self):
        super().__init__(
            code="UNAUTHORIZED",
            message="Not authorized to cancel this booking.",
            status_code=403
        )

class AlreadyCancelledError(AppError):
    def __init__(self):
        super().__init__(
            code="ALREADY_CANCELLED",
            message="Booking is already cancelled.",
            status_code=422
        )