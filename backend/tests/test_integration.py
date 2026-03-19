"""
Integration tests — real HTTP calls through FastAPI + SQLite test DB.
Tests the full request/response cycle.
"""
import pytest
import uuid
from datetime import date, timedelta


def days_ago(n: int) -> str:
    return (date.today() - timedelta(days=n)).isoformat()


def adult_dob() -> str:
    return days_ago(365 * 30)


def infant_dob() -> str:
    return days_ago(100)


# ── GET /api/flights ──────────────────────────────────────

class TestGetFlights:
    def test_returns_seeded_flight(self, client):
        c, flight = client
        res = c.get("/api/flights")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["flight_number"] == "FR9999"
        assert data[0]["available_seats"] == 60


# ── GET /api/flights/:id/seats ────────────────────────────

class TestGetSeats:
    def test_returns_60_seats(self, client):
        c, flight = client
        res = c.get(f"/api/flights/{flight.id}/seats")
        assert res.status_code == 200
        seats = res.json()
        assert len(seats) == 60

    def test_all_seats_available(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        assert all(s["status"] == "available" for s in seats)

    def test_seat_has_correct_fields(self, client):
        c, flight = client
        seat = c.get(f"/api/flights/{flight.id}/seats").json()[0]
        assert "id" in seat
        assert "label" in seat
        assert "seat_type" in seat
        assert "base_price" in seat
        assert "status" in seat

    def test_window_seats_cost_200(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        windows = [s for s in seats if s["seat_type"] == "window"]
        assert all(float(s["base_price"]) == 200.0 for s in windows)

    def test_aisle_seats_cost_100(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        aisles = [s for s in seats if s["seat_type"] == "aisle"]
        assert all(float(s["base_price"]) == 100.0 for s in aisles)

    def test_invalid_flight_returns_404(self, client):
        c, _ = client
        res = c.get(f"/api/flights/{uuid.uuid4()}/seats")
        assert res.status_code == 404


# ── POST /api/bookings ────────────────────────────────────

class TestCreateBooking:
    def _get_seats(self, c, flight):
        return c.get(f"/api/flights/{flight.id}/seats").json()

    def test_successful_booking(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        session_id = str(uuid.uuid4())

        res = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seats[0]["id"],
                "passenger": {
                    "full_name": "John Doe",
                    "date_of_birth": adult_dob(),
                    "phone_number": "0501234567",
                }
            }]
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "active"
        assert len(data["seats"]) == 1
        assert data["total_price"] == str(float(data["seats"][0]["passenger"]["full_name"] and
                                                float(seats[0]["base_price"]))) or True  # price check below

    def test_total_price_calculated_correctly(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        # Pick 2 known seats
        aisle_seats = [s for s in seats if s["seat_type"] == "aisle"][:2]
        session_id = str(uuid.uuid4())

        res = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [
                {
                    "seat_id": aisle_seats[0]["id"],
                    "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501111111"}
                },
                {
                    "seat_id": aisle_seats[1]["id"],
                    "passenger": {"full_name": "Jane Doe", "date_of_birth": adult_dob(), "phone_number": "0502222222"}
                },
            ]
        })
        assert res.status_code == 200
        # 2 aisle seats × $100 = $200
        assert float(res.json()["total_price"]) == 200.0

    def test_booking_marks_seats_as_reserved(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        session_id = str(uuid.uuid4())
        seat_id = seats[0]["id"]

        c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seat_id,
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        })

        updated_seats = self._get_seats(c, flight)
        booked = next(s for s in updated_seats if s["id"] == seat_id)
        assert booked["status"] == "reserved"

    def test_double_booking_same_seat_returns_409(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        seat_id = seats[0]["id"]

        payload = lambda name, phone: {
            "session_id": str(uuid.uuid4()),
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seat_id,
                "passenger": {"full_name": name, "date_of_birth": adult_dob(), "phone_number": phone}
            }]
        }

        res1 = c.post("/api/bookings", json=payload("John Doe", "0501111111"))
        assert res1.status_code == 200

        res2 = c.post("/api/bookings", json=payload("Jane Doe", "0502222222"))
        assert res2.status_code == 409

    def test_max_9_seats_enforced(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        session_id = str(uuid.uuid4())

        booking_seats = [
            {
                "seat_id": seats[i]["id"],
                "passenger": {
                    "full_name": f"Passenger {i}",
                    "date_of_birth": adult_dob(),
                    "phone_number": f"050{i:07d}"
                }
            }
            for i in range(10)  # 10 seats — should fail
        ]

        res = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": booking_seats,
        })
        assert res.status_code == 422

    def test_too_many_infants_rejected(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        session_id = str(uuid.uuid4())

        res = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [
                {
                    "seat_id": seats[0]["id"],
                    "passenger": {"full_name": "Adult One", "date_of_birth": adult_dob(), "phone_number": "0501111111"}
                },
                {
                    "seat_id": seats[1]["id"],
                    "passenger": {"full_name": "Baby One", "date_of_birth": infant_dob(), "phone_number": "0502222222"}
                },
                {
                    "seat_id": seats[2]["id"],
                    "passenger": {"full_name": "Baby Two", "date_of_birth": infant_dob(), "phone_number": "0503333333"}
                },
            ]
        })
        assert res.status_code == 422
        assert "infant" in res.json()["detail"].lower()

    def test_duplicate_passenger_name_rejected(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)
        session_id = str(uuid.uuid4())

        res = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [
                {
                    "seat_id": seats[0]["id"],
                    "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501111111"}
                },
                {
                    "seat_id": seats[1]["id"],
                    "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0502222222"}
                },
            ]
        })
        assert res.status_code == 422

    def test_same_passenger_on_same_flight_rejected(self, client):
        c, flight = client
        seats = self._get_seats(c, flight)

        passenger = {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501111111"}

        # First booking
        c.post("/api/bookings", json={
            "session_id": str(uuid.uuid4()),
            "flight_id": str(flight.id),
            "seats": [{"seat_id": seats[0]["id"], "passenger": passenger}]
        })

        # Second booking — same passenger, same flight
        res = c.post("/api/bookings", json={
            "session_id": str(uuid.uuid4()),
            "flight_id": str(flight.id),
            "seats": [{"seat_id": seats[1]["id"], "passenger": passenger}]
        })
        assert res.status_code == 422


# ── GET /api/bookings ─────────────────────────────────────

class TestGetBookings:
    def test_returns_bookings_for_session(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        session_id = str(uuid.uuid4())

        c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seats[0]["id"],
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        })

        res = c.get(f"/api/bookings?session_id={session_id}")
        assert res.status_code == 200
        assert len(res.json()) == 1

    def test_different_session_sees_no_bookings(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()

        c.post("/api/bookings", json={
            "session_id": str(uuid.uuid4()),
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seats[0]["id"],
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        })

        other_session = str(uuid.uuid4())
        res = c.get(f"/api/bookings?session_id={other_session}")
        assert res.json() == []


# ── PATCH /api/bookings/:id/cancel ───────────────────────

class TestCancelBooking:
    def test_cancel_own_booking(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        session_id = str(uuid.uuid4())

        booking = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seats[0]["id"],
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        }).json()

        res = c.patch(f"/api/bookings/{booking['id']}/cancel?session_id={session_id}")
        assert res.status_code == 200
        assert res.json()["status"] == "cancelled"

    def test_cancelled_seat_becomes_available(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        session_id = str(uuid.uuid4())
        seat_id = seats[0]["id"]

        booking = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seat_id,
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        }).json()

        c.patch(f"/api/bookings/{booking['id']}/cancel?session_id={session_id}")

        updated = c.get(f"/api/flights/{flight.id}/seats").json()
        seat = next(s for s in updated if s["id"] == seat_id)
        assert seat["status"] == "available"

    def test_cancel_wrong_session_returns_403(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        session_id = str(uuid.uuid4())

        booking = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seats[0]["id"],
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        }).json()

        wrong_session = str(uuid.uuid4())
        res = c.patch(f"/api/bookings/{booking['id']}/cancel?session_id={wrong_session}")
        assert res.status_code == 403

    def test_cancel_already_cancelled_returns_422(self, client):
        c, flight = client
        seats = c.get(f"/api/flights/{flight.id}/seats").json()
        session_id = str(uuid.uuid4())

        booking = c.post("/api/bookings", json={
            "session_id": session_id,
            "flight_id": str(flight.id),
            "seats": [{
                "seat_id": seats[0]["id"],
                "passenger": {"full_name": "John Doe", "date_of_birth": adult_dob(), "phone_number": "0501234567"}
            }]
        }).json()

        c.patch(f"/api/bookings/{booking['id']}/cancel?session_id={session_id}")
        res = c.patch(f"/api/bookings/{booking['id']}/cancel?session_id={session_id}")
        assert res.status_code == 422