"""
test_oilseed_recommendation.py -- Unit tests for Oilseed-First Recommendation Engine.
"""
import pytest
from app.models import User, UserRole, Farm, Crop, CropType
from app.decision_engine.recommendation import evaluate_all_oilseeds, generate_recommendation


def test_evaluate_all_oilseeds_returns_top_10(db_session, farmer_user_token):
    # Evaluate for golden demo farm (farm_id = 1)
    results = evaluate_all_oilseeds(db_session, farm_id=1)
    assert len(results) > 0
    assert len(results) <= 10

    # Verify rank ordering
    for i, res in enumerate(results):
        assert res["rank"] == i + 1
        assert "crop_name" in res
        assert "farm_suitability_score" in res
        assert "water_suitability_score" in res
        assert "economic_potential_score" in res
        assert "overall_score" in res
        assert "decision" in res
        assert 0 <= res["farm_suitability_score"] <= 100
        assert 0 <= res["water_suitability_score"] <= 100
        assert 0 <= res["economic_potential_score"] <= 100
        assert 0 <= res["overall_score"] <= 100


def test_recommendation_api_returns_component_scores_and_top_oilseeds(client, farmer_user_token):
    token = farmer_user_token["token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/recommendations",
        json={"farm_id": 1},
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()

    assert "recommended_crop" in data
    assert "farm_suitability_score" in data
    assert "water_suitability_score" in data
    assert "economic_potential_score" in data
    assert "overall_score" in data
    assert "top_oilseeds" in data
    assert isinstance(data["top_oilseeds"], list)
    assert len(data["top_oilseeds"]) > 0

    best = data["top_oilseeds"][0]
    assert best["rank"] == 1
    assert best["crop_name"] == data["recommended_crop"]


def test_different_farm_inputs_produce_different_rankings(db_session):
    # Farm 1 (Tumkur, 1.0 acre, red laterite, water available)
    res1 = evaluate_all_oilseeds(db_session, farm_id=1)
    # Farm 3 (Dharwad, 3.0 acre, red laterite, no water)
    res3 = evaluate_all_oilseeds(db_session, farm_id=3)

    assert len(res1) > 0
    assert len(res3) > 0
    # Confirm top crop or score breakdown reflects different farm conditions
    top1 = res1[0]["crop_name"]
    top3 = res3[0]["crop_name"]
    # At least scores or rankings differ
    assert (top1 != top3) or (res1[0]["water_suitability_score"] != res3[0]["water_suitability_score"])


def test_agronomic_suitability_remains_primary(db_session):
    results = evaluate_all_oilseeds(db_session, farm_id=1)
    # Ensure #1 crop has high suitability
    best = results[0]
    assert best["farm_suitability_score"] >= 50
