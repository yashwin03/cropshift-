"""
test_golden_demo.py -- A15 Golden Demo contract test suite.
Asserts the exact parameters and outputs for Farm 1.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_golden_demo_recommendation():
    # 1. POST /api/v1/recommendations for Farm 1
    res = client.post("/api/v1/recommendations", json={"farm_id": 1})
    assert res.status_code == 200
    data = res.json()

    assert data["recommended_crop"] == "Groundnut"
    assert data["suitability_score"] == 87
    assert data["profitability_score"] == 76
    assert data["market_score"] == 90
    assert data["risk_score"] == 28
    assert data["safety_score"] == 82
    assert data["decision"] == "SWITCH"
    assert data["expected_profit"] == 43000
    assert data["current_crop_profit"] == 34000
    assert data["profit_difference"] == 9000


def test_golden_demo_profitability():
    # 2. GET /api/v1/profitability/1
    res = client.get("/api/v1/profitability/1")
    assert res.status_code == 200
    data = res.json()

    assert data["current_crop"]["crop_name"] == "Paddy"
    assert data["current_crop"]["estimated_profit"] == 34000
    assert data["recommended_crop"]["crop_name"] == "Groundnut"
    assert data["recommended_crop"]["estimated_profit"] == 43000
    assert data["profit_difference"] == 9000


def test_golden_demo_risk_simulation():
    # 3. POST /api/v1/risk-simulation for Farm 1 and Groundnut (Crop 2)
    res = client.post("/api/v1/risk-simulation", json={"farm_id": 1, "crop_id": 2})
    assert res.status_code == 200
    data = res.json()

    # baseline
    assert data["baseline"]["safety_score"] == 82
    assert data["baseline"]["decision"] == "SWITCH"

    # price_down
    assert data["price_down"]["safety_score"] == 69
    assert data["price_down"]["decision"] == "CAUTION"

    # yield_down
    assert data["yield_down"]["safety_score"] == 63
    assert data["yield_down"]["decision"] == "CAUTION"

    # water_risk
    assert data["water_risk"]["safety_score"] == 48
    assert data["water_risk"]["decision"] == "DONT_SWITCH"


def test_golden_demo_ivr():
    # 4. POST /api/v1/ivr/recommendation for Farmer 1
    res = client.post("/api/v1/ivr/recommendation", json={"farmer_id": 1})
    assert res.status_code == 200
    data = res.json()

    assert data["verified"] is True
    assert data["farmer_name"] == "Raju Naik"
    assert "Namaste Raju Naik" in data["voice_script"]
    assert "groundnut" in data["voice_script"].lower()
    assert "eighty two" in data["voice_script"].lower()
    assert "nine thousand" in data["voice_script"].lower()

    rec = data["recommendation"]
    assert rec["recommended_crop"] == "Groundnut"
    assert rec["safety_score"] == 82
    assert rec["decision"] == "SWITCH"
