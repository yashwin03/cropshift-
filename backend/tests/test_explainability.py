"""
test_explainability.py -- A9 acceptance tests for Explainability engine.
"""
import pytest
from app.decision_engine.explainability import generate_explanations


def test_explainability_switch():
    reasons, risks = generate_explanations(
        decision="SWITCH",
        suitability_score=87,
        profitability_score=84,
        market_score=78,
        risk_score=30,
        profit_diff=11000.0,
        current_crop_profit=32000.0,
        expected_profit=43000.0,
        alt_crop_name="Groundnut",
        water_requirement="MEDIUM",
        water_availability=True,
        trend="RISING",
        distance_km=0.28,
        notes=[]
    )
    
    # Check bounds
    assert 3 <= len(reasons) <= 5
    assert 1 <= len(risks) <= 4

    # Check SWITCH specific keywords
    assert any("11,000" in r for r in reasons)
    assert any("87/100" in r for r in reasons)
    assert any("78/100" in r for r in reasons)
    assert any("switch is highly recommended" in r.lower() for r in reasons)


def test_explainability_caution():
    reasons, risks = generate_explanations(
        decision="CAUTION",
        suitability_score=87,
        profitability_score=76,
        market_score=90,
        risk_score=28,
        profit_diff=9000.0,
        current_crop_profit=34000.0,
        expected_profit=43000.0,
        alt_crop_name="Groundnut",
        water_requirement="MEDIUM",
        water_availability=True,
        trend="RISING",
        distance_km=0.28,
        notes=[]
    )

    assert 3 <= len(reasons) <= 5
    assert 1 <= len(risks) <= 4

    # Check CAUTION specific mixed signals
    assert any("mixed signals" in r.lower() for r in reasons)
    assert any("87/100" in r for r in reasons)
    assert any("28/100" in r for r in reasons)


def test_explainability_dont_switch():
    reasons, risks = generate_explanations(
        decision="DONT_SWITCH",
        suitability_score=50,
        profitability_score=40,
        market_score=45,
        risk_score=70,
        profit_diff=-2000.0,
        current_crop_profit=30000.0,
        expected_profit=28000.0,
        alt_crop_name="Sunflower",
        water_requirement="HIGH",
        water_availability=False,
        trend="FALLING",
        distance_km=120.0,
        notes=[]
    )

    assert 3 <= len(reasons) <= 5
    assert 1 <= len(risks) <= 4

    # Check DONT_SWITCH negative indicators
    assert any("do not recommend switching" in r.lower() for r in reasons)
    assert any("-2,000" in r for r in reasons)
    assert any("50/100" in r for r in reasons)


def test_explainability_confidence_warnings():
    reasons, _ = generate_explanations(
        decision="SWITCH",
        suitability_score=80,
        profitability_score=70,
        market_score=60,
        risk_score=40,
        profit_diff=5000.0,
        current_crop_profit=30000.0,
        expected_profit=35000.0,
        alt_crop_name="Maize",
        water_requirement="MEDIUM",
        water_availability=True,
        trend="STABLE",
        distance_km=15.0,
        notes=[
            "Soil type data is missing; fallback to neutral default.",
            "Water compatibility details not available; neutral default used."
        ]
    )

    # Check for confidence warning notes in the reasons
    assert any("soil information was not available" in r.lower() for r in reasons)
    assert any("water availability details not available" in r.lower() for r in reasons)
