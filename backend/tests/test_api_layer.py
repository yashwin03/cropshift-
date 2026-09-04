"""
test_api_layer.py -- A12 acceptance tests for API layer endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_v1_health():
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_recommendations_endpoint():
    res = client.post("/api/v1/recommendations", json={"farm_id": 1})
    assert res.status_code == 200
    data = res.json()
    
    # Assert exact key contract
    expected_keys = {
        "recommended_crop", "suitability_score", "profitability_score",
        "market_score", "risk_score", "safety_score", "decision",
        "expected_profit", "current_crop_profit", "profit_difference",
        "reasons", "risks"
    }
    assert expected_keys.issubset(set(data.keys()))


def test_profitability_endpoint():
    res = client.get("/api/v1/profitability/1")
    assert res.status_code == 200
    data = res.json()
    
    expected_keys = {
        "current_crop", "recommended_crop", "expected_yield",
        "production_cost", "expected_revenue", "estimated_profit",
        "profit_difference"
    }
    assert set(data.keys()) == expected_keys
    
    crop_keys = {
        "crop_id", "crop_name", "expected_yield", "yield_unit",
        "production_cost", "expected_revenue", "estimated_profit",
        "data_status"
    }
    assert set(data["current_crop"].keys()) == crop_keys
    assert set(data["recommended_crop"].keys()) == crop_keys


def test_markets_endpoint():
    res = client.get("/api/v1/markets/2?farm_id=1")
    assert res.status_code == 200
    data = res.json()
    
    expected_keys = {
        "crop_id", "crop_name", "price", "price_unit", "market_name",
        "market_location", "distance_km", "trend", "market_score",
        "data_status", "data_source"
    }
    assert set(data.keys()) == expected_keys


def test_subsidies_endpoint():
    res = client.get("/api/v1/subsidies/1")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 5
    
    expected_keys = {
        "scheme_id", "scheme_name", "relevance", "eligibility_status",
        "eligibility_factors", "required_information", "support_information",
        "verification_required", "data_source"
    }
    for s in data:
        assert set(s.keys()) == expected_keys


def test_geospatial_endpoint():
    res = client.get("/api/v1/geospatial/1")
    assert res.status_code == 200
    data = res.json()
    
    expected_keys = {
        "farm", "nearby_markets", "distance_information", "geographic_context"
    }
    assert set(data.keys()) == expected_keys
    
    # Coordinates check
    assert "latitude" in data["farm"]
    assert "longitude" in data["farm"]


def test_risk_simulation_endpoint():
    res = client.post("/api/v1/risk-simulation", json={"farm_id": 1, "crop_id": 2})
    assert res.status_code == 200
    data = res.json()
    
    expected_keys = {"baseline", "price_down", "yield_down", "water_risk"}
    assert set(data.keys()) == expected_keys
    
    scenario_keys = {"safety_score", "decision"}
    for scenario in data.values():
        assert set(scenario.keys()) == scenario_keys

    # Assert Golden Demo expected values
    assert data["baseline"]["safety_score"] == 82
    assert data["baseline"]["decision"] == "SWITCH"
    assert data["price_down"]["safety_score"] == 69
    assert data["price_down"]["decision"] == "CAUTION"
    assert data["yield_down"]["safety_score"] == 63
    assert data["yield_down"]["decision"] == "CAUTION"
    assert data["water_risk"]["safety_score"] == 48
    assert data["water_risk"]["decision"] == "DONT_SWITCH"


def test_ivr_endpoint():
    res = client.post("/api/v1/ivr/recommendation", json={"farmer_id": 1})
    assert res.status_code == 200
    data = res.json()
    
    assert "recommendation" in data
    rec_keys = {
        "recommended_crop", "suitability_score", "profitability_score",
        "market_score", "risk_score", "safety_score", "decision",
        "expected_profit", "current_crop_profit", "profit_difference",
        "reasons", "risks"
    }
    assert rec_keys.issubset(set(data["recommendation"].keys()))


def test_invalid_farm_id_404():
    res = client.get("/api/v1/profitability/9999")
    assert res.status_code == 404
