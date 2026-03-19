from uuid import UUID
from fastapi import Header, HTTPException


def get_session_id(x_session_id: str = Header(...)) -> UUID:
    try:
        return UUID(x_session_id)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=400, detail="Invalid or missing session ID")