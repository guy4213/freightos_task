"""
Unit tests — pure business logic, no DB or HTTP calls.
Tests the service-layer functions directly.
"""
import pytest
from datetime import date, timedelta
from fastapi import HTTPException
from unittest.mock import MagicMock

from app.services.booking_service import (
    _is_infant,
    _calculate_age,
    _validate_infant_adult_ratio,
)
from app.schemas import SeatBookingIn, PassengerIn


# ── Helpers ──────────────────────────────────────────────

def make_passenger(full_name: str, dob: date, phone: str) -> SeatBookingIn:
    import uuid
    return SeatBookingIn(
        seat_id=uuid.uuid4(),
        passenger=PassengerIn(
            full_name=full_name,
            date_of_birth=dob,
            phone_number=phone,
        )
    )


def days_ago(n: int) -> date:
    return date.today() - timedelta(days=n)


# ── Age / Infant detection ────────────────────────────────

class TestInfantDetection:
    def test_newborn_is_infant(self):
        assert _is_infant(days_ago(30)) is True

    def test_one_year_old_is_infant(self):
        assert _is_infant(days_ago(365)) is True

    def test_exactly_two_years_is_not_infant(self):
        assert _is_infant(days_ago(365 * 2 + 1)) is False

    def test_adult_is_not_infant(self):
        assert _is_infant(days_ago(365 * 30)) is False

    def test_teenager_is_not_infant(self):
        assert _is_infant(days_ago(365 * 15)) is False


class TestCalculateAge:
    def test_30_year_old(self):
        dob = date.today().replace(year=date.today().year - 30)
        assert _calculate_age(dob) == 30

    def test_newborn(self):
        assert _calculate_age(days_ago(10)) == 0


# ── Infant/Adult ratio validation ────────────────────────

class TestInfantAdultRatio:
    def test_one_adult_passes(self):
        items = [make_passenger("John Doe", days_ago(365 * 30), "0501111111")]
        _validate_infant_adult_ratio(items)  # should not raise

    def test_one_infant_one_adult_passes(self):
        items = [
            make_passenger("John Doe", days_ago(365 * 30), "0501111111"),
            make_passenger("Baby Doe", days_ago(100), "0502222222"),
        ]
        _validate_infant_adult_ratio(items)  # should not raise

    def test_two_infants_two_adults_passes(self):
        items = [
            make_passenger("Adult One", days_ago(365 * 25), "0501111111"),
            make_passenger("Adult Two", days_ago(365 * 28), "0502222222"),
            make_passenger("Baby One",  days_ago(100), "0503333333"),
            make_passenger("Baby Two",  days_ago(200), "0504444444"),
        ]
        _validate_infant_adult_ratio(items)  # should not raise

    def test_two_infants_one_adult_fails(self):
        items = [
            make_passenger("Adult One", days_ago(365 * 25), "0501111111"),
            make_passenger("Baby One",  days_ago(100), "0502222222"),
            make_passenger("Baby Two",  days_ago(200), "0503333333"),
        ]
        with pytest.raises(HTTPException) as exc:
            _validate_infant_adult_ratio(items)
        assert exc.value.status_code == 422
        assert "infant" in exc.value.detail.lower()

    def test_infant_only_fails(self):
        items = [make_passenger("Baby", days_ago(100), "0501111111")]
        with pytest.raises(HTTPException) as exc:
            _validate_infant_adult_ratio(items)
        assert exc.value.status_code == 422


# ── Duplicate passenger validation (tested via API in integration tests) ─────
# _validate_no_duplicate_passengers is tested end-to-end in test_integration.py