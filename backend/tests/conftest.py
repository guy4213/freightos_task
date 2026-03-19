import pytest
import uuid
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.seed import COLUMN_CONFIG
from app.models import Flight, Seat

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

    session_id = str(uuid.uuid4())
    test_client = TestClient(app, headers={"X-Session-ID": session_id})

    yield test_client, flight, session_id

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()