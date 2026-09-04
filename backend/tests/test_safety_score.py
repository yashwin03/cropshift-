"""
test_safety_score.py -- A6 acceptance tests for safety score / risk engine.
"""
import pytest
from app.decision_engine.risk import RiskFactor
from app.decision_engine.safety_score import calculate_safety_score, SafetyResult


def test_safety_score_no_risks():
    # No risks -> safety_score = 100, confidence = MEDIUM, note added
    res = calculate_safety_score([])
    assert res.safety_score == 100
    assert res.weighted_risk == 0.0
    assert res.confidence == "MEDIUM"
    assert len(res.notes) == 1
    assert "No hazards were assessed." in res.notes


def test_safety_score_single_factor():
    # Single risk factor with raw_risk_level = 0.40 and weight = 1.0 -> safety_score = 60
    rf = RiskFactor(name="Water Stress", raw_risk_level=0.40, weight=1.0)
    res = calculate_safety_score([rf])
    assert res.safety_score == 60
    assert res.weighted_risk == 0.40
    assert res.confidence == "HIGH"
    assert len(res.notes) == 0


def test_safety_score_multiple_factors():
    # Weighted risk = (0.2 * 1.0 + 0.8 * 0.5) / (1.0 + 0.5) = (0.2 + 0.4) / 1.5 = 0.6 / 1.5 = 0.40
    # Safety score = (1.0 - 0.4) * 100 = 60
    rf1 = RiskFactor(name="Price Volatility", raw_risk_level=0.20, weight=1.0)
    rf2 = RiskFactor(name="Water Stress", raw_risk_level=0.80, weight=0.5)
    res = calculate_safety_score([rf1, rf2])
    assert res.safety_score == 60
    assert pytest.approx(res.weighted_risk) == 0.40
    assert res.confidence == "HIGH"


def test_safety_score_zero_weight_sum():
    # sum(weights) = 0 -> weighted_risk = 0.0, safety_score = 100
    rf = RiskFactor(name="Price Volatility", raw_risk_level=0.50, weight=0.0)
    res = calculate_safety_score([rf])
    assert res.safety_score == 100
    assert res.weighted_risk == 0.0


def test_safety_score_determinism():
    rf1 = RiskFactor(name="Price Volatility", raw_risk_level=0.35, weight=0.8)
    rf2 = RiskFactor(name="Water Stress", raw_risk_level=0.15, weight=0.4)
    
    first = calculate_safety_score([rf1, rf2])
    for _ in range(100):
        res = calculate_safety_score([rf1, rf2])
        assert res.safety_score == first.safety_score
        assert res.weighted_risk == first.weighted_risk
        assert res.confidence == first.confidence
        assert res.notes == first.notes
