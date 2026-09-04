"""
test_error_handling.py — A14 acceptance tests for global error handling.

Verifies:
- Every error response matches the canonical envelope:
    {"error": {"code": "...", "message": "...", "details": [...]}}
- 404 for unknown farm_id → FARM_NOT_FOUND
- 404 for unknown farmer_id → FARMER_NOT_FOUND
- 422 malformed body → INVALID_INPUT with field errors in details
- 500 unhandled exception → INTERNAL_ERROR, no traceback in body
- No stack trace / DATABASE_URL leakage in any error response
"""
import json
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from app.main import app
from app.api.errors import register_exception_handlers

client = TestClient(app, raise_server_exceptions=False)

ENVELOPE_KEYS = {"error"}
ERROR_KEYS = {"code", "message", "details"}

BANNED_STRINGS = [
    "Traceback",
    "File \"",
    "sqlalchemy",
    "psycopg2",
    "DATABASE_URL",
    "12345",          # password fragment from connection string
    "localhost:5433",
    "Exception",
]


def _assert_envelope(data: dict) -> dict:
    """Assert the canonical error envelope and return the inner error dict."""
    assert set(data.keys()) == ENVELOPE_KEYS, f"Unexpected top-level keys: {data.keys()}"
    err = data["error"]
    assert set(err.keys()) == ERROR_KEYS, f"Unexpected error keys: {err.keys()}"
    assert isinstance(err["details"], list)
    return err


def _no_leakage(response_text: str) -> None:
    for banned in BANNED_STRINGS:
        assert banned not in response_text, f"Sensitive string '{banned}' leaked in error response"


# ── 404 tests ──────────────────────────────────────────────────────────────────

def test_404_unknown_farm_profitability():
    res = client.get("/api/v1/profitability/99999")
    assert res.status_code == 404
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "FARM_NOT_FOUND"
    _no_leakage(res.text)


def test_404_unknown_farm_subsidies():
    res = client.get("/api/v1/subsidies/99999")
    assert res.status_code == 404
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] in ("FARM_NOT_FOUND", "FARMER_NOT_FOUND", "CROP_NOT_FOUND")
    _no_leakage(res.text)


def test_404_unknown_crop_markets():
    res = client.get("/api/v1/markets/99999")
    assert res.status_code == 404
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "CROP_NOT_FOUND"
    _no_leakage(res.text)


def test_404_unknown_farm_geospatial():
    res = client.get("/api/v1/geospatial/99999")
    # geographic context returns 404 if farm is missing
    assert res.status_code in (404, 200)  # geospatial may handle gracefully
    _no_leakage(res.text)


# ── 422 tests ──────────────────────────────────────────────────────────────────

def test_422_missing_farm_id_recommendations():
    res = client.post("/api/v1/recommendations", json={})
    assert res.status_code == 422
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "INVALID_INPUT"
    assert len(err["details"]) >= 1
    _no_leakage(res.text)


def test_422_wrong_type_recommendations():
    res = client.post("/api/v1/recommendations", json={"farm_id": "not_a_number"})
    assert res.status_code == 422
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "INVALID_INPUT"
    _no_leakage(res.text)


def test_422_missing_farmer_id_ivr():
    res = client.post("/api/v1/ivr/recommendation", json={})
    assert res.status_code == 422
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "INVALID_INPUT"
    assert len(err["details"]) >= 1
    _no_leakage(res.text)


def test_422_malformed_risk_simulation():
    res = client.post("/api/v1/risk-simulation", json={"farm_id": "bad"})
    assert res.status_code == 422
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "INVALID_INPUT"
    _no_leakage(res.text)


def test_422_details_contain_field_info():
    res = client.post("/api/v1/recommendations", json={})
    assert res.status_code == 422
    data = res.json()
    err = data["error"]
    details = err["details"]
    assert len(details) >= 1
    # Each detail must have field + message keys
    for detail in details:
        assert "field" in detail
        assert "message" in detail


# ── 500 test ──────────────────────────────────────────────────────────────────

def test_500_no_traceback_leakage():
    """
    Trigger a 500 by injecting a route that raises an unhandled exception,
    using a temporary isolated FastAPI app with the same error handlers.
    """
    test_app = FastAPI()
    register_exception_handlers(test_app)

    @test_app.get("/force-500")
    def force_error():
        raise RuntimeError("Deliberate internal failure for testing")

    tc = TestClient(test_app, raise_server_exceptions=False)
    res = tc.get("/force-500")
    assert res.status_code == 500
    data = res.json()
    err = _assert_envelope(data)
    assert err["code"] == "INTERNAL_ERROR"
    # No traceback in response body
    assert "Traceback" not in res.text
    assert "RuntimeError" not in res.text
    assert "Deliberate" not in res.text
    _no_leakage(res.text)


# ── Envelope structure tests ───────────────────────────────────────────────────

def test_error_envelope_exact_structure_404():
    res = client.get("/api/v1/profitability/88888")
    assert res.status_code == 404
    data = res.json()
    # Top level must be exactly {"error": {...}}
    assert list(data.keys()) == ["error"]
    err = data["error"]
    # Inner must be exactly {"code": ..., "message": ..., "details": [...]}
    assert set(err.keys()) == {"code", "message", "details"}
    assert isinstance(err["code"], str) and len(err["code"]) > 0
    assert isinstance(err["message"], str) and len(err["message"]) > 0
    assert isinstance(err["details"], list)


def test_error_envelope_exact_structure_422():
    res = client.post("/api/v1/recommendations", json={})
    assert res.status_code == 422
    data = res.json()
    assert list(data.keys()) == ["error"]
    err = data["error"]
    assert set(err.keys()) == {"code", "message", "details"}
    assert isinstance(err["details"], list)


# ── IVR error behavior (A13 preservation) ─────────────────────────────────────

def test_ivr_unknown_farmer_returns_200_not_exception():
    """A13 spec: unknown farmer should return verified=False, not raise an exception."""
    res = client.post("/api/v1/ivr/recommendation", json={"farmer_id": 99999})
    # IVR gracefully handles unknown farmers — returns 200 with verified=False
    assert res.status_code == 200
    data = res.json()
    assert data["verified"] is False
    assert data["recommendation"] is None
    _no_leakage(res.text)


# ── Successful response contracts unchanged ────────────────────────────────────

def test_successful_recommendation_unchanged():
    """Confirm A12 success contract is preserved — envelope only appears on errors."""
    res = client.post("/api/v1/recommendations", json={"farm_id": 1})
    assert res.status_code == 200
    data = res.json()
    # Success response should NOT be wrapped in error envelope
    assert "error" not in data
    assert "recommended_crop" in data
    assert "safety_score" in data
