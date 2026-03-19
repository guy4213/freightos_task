import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.seed import COLUMN_CONFIG, FLIGHTS_DATA
from app.models import Flight, Seat

from datetime import datetime, timedelta
import uuid

# ── Use SQLite in-memory for tests (no Postgres needed) ──
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db

    # Seed one flight with 60 seats
    flight = Flight(
        id=uuid.uuid4(),
        flight_number="FR9999",
        origin="TLV",
        destination="LHR",
        departure_at=datetime.utcnow() + timedelta(days=3),
        arrival_at=datetime.utcnow() + timedelta(days=3, hours=5),
    )
    db.add(flight)
    db.flush()

    for row in range(1, 11):
        for col in ["A", "B", "C", "D", "E", "F"]:
            seat_type, base_price = COLUMN_CONFIG[col]
            db.add(Seat(
                flight_id=flight.id,
                row_number=row,
                column_letter=col,
                seat_type=seat_type,
                base_price=base_price,
            ))
    db.commit()

    yield TestClient(app), flight

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()