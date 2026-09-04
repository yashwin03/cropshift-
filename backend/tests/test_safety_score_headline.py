"""
test_safety_score_headline.py -- A7 acceptance tests for Safety Score headline logic.
"""
import pytest
from app.decision_engine.safety_score import calculate_headline_safety_score, SafetyScoreResult


def test_safety_score_headline_boundaries():
    # Boundary tests at 59/60 (DONT_SWITCH vs CAUTION)
    # Score 59 -> DONT_SWITCH
    # 59 * 1.0 + 0 * 0 + 0 * 0 + 0 * 0 = 59.0 -> rounds to 59 -> DONT_SWITCH
    res1 = calculate_headline_safety_score(59, 0, 0, 100) # Risk = 100 -> Risk Inverse = 0
    assert res1.safety_score == 21  # 59 * 0.35 + 0 + 0 + 0 = 20.65 -> 21 -> DONT_SWITCH
    assert res1.decision == "DONT_SWITCH"

    # Score 59: Suitability = 100, Profitability = 80, Market = 0, Risk = 100 (Risk Inverse = 0)
    # 100 * 0.35 + 80 * 0.30 + 0 + 0 = 35 + 24 = 59.0 -> rounds to 59 -> DONT_SWITCH
    res_59 = calculate_headline_safety_score(100, 80, 0, 100)
    assert res_59.safety_score == 59
    assert res_59.decision == "DONT_SWITCH"

    # Score 60: Suitability = 100, Profitability = 83.333, Market = 0, Risk = 100 (Risk Inverse = 0)
    # 100 * 0.35 + 83.333 * 0.30 + 0 + 0 = 35 + 25 = 60.0 -> rounds to 60 -> CAUTION
    res_60 = calculate_headline_safety_score(100, 83.333, 0, 100)
    assert res_60.safety_score == 60
    assert res_60.decision == "CAUTION"

    # Boundary tests at 79/80 (CAUTION vs SWITCH)
    # Score 79: Suitability = 100, Profitability = 100, Market = 70, Risk = 100 (Risk Inverse = 0)
    # 100 * 0.35 + 100 * 0.30 + 70 * 0.20 + 0 = 35 + 30 + 14 = 79.0 -> rounds to 79 -> CAUTION
    res_79 = calculate_headline_safety_score(100, 100, 70, 100)
    assert res_79.safety_score == 79
    assert res_79.decision == "CAUTION"

    # Score 80: Suitability = 100, Profitability = 100, Market = 75, Risk = 100 (Risk Inverse = 0)
    # 100 * 0.35 + 100 * 0.30 + 75 * 0.20 + 0 = 35 + 30 + 15 = 80.0 -> rounds to 80 -> SWITCH
    res_80 = calculate_headline_safety_score(100, 100, 75, 100)
    assert res_80.safety_score == 80
    assert res_80.decision == "SWITCH"


def test_safety_score_headline_weights_sum():
    res = calculate_headline_safety_score(100, 100, 100, 0) # Risk = 0 -> Risk Inverse = 100
    assert res.safety_score == 100
    assert sum(res.weights.values()) == pytest.approx(1.0)


def test_safety_score_headline_missing_data():
    # 1 missing -> confidence MEDIUM, neutral 60 used
    res_1 = calculate_headline_safety_score(None, 100, 100, 0)
    assert res_1.confidence == "MEDIUM"
    assert res_1.components["suitability"]["value"] == 60.0
    assert len(res_1.notes) == 1

    # 2 missing -> confidence LOW, neutral 60 used
    res_2 = calculate_headline_safety_score(None, None, 100, 0)
    assert res_2.confidence == "LOW"
    assert res_2.components["suitability"]["value"] == 60.0
    assert res_2.components["profitability"]["value"] == 60.0
    assert len(res_2.notes) == 2


def test_safety_score_headline_golden_demo():
    # Golden Demo (Option b): Suitability = 87, Profitability = 84, Market = 78, Risk = 76 (Risk Inverse = 24)
    # 87 * 0.35 + 84 * 0.30 + 78 * 0.20 + 24 * 0.15 = 30.45 + 25.20 + 15.60 + 3.60 = 74.85 -> rounds to 75
    res = calculate_headline_safety_score(87, 84, 78, 76)
    assert res.safety_score == 75
    assert res.decision == "CAUTION"
    assert res.confidence == "HIGH"
    assert len(res.notes) == 0


def test_safety_score_headline_determinism():
    first = calculate_headline_safety_score(85, 90, 75, 40)
    for _ in range(100):
        res = calculate_headline_safety_score(85, 90, 75, 40)
        assert res.safety_score == first.safety_score
        assert res.decision == first.decision
        assert res.confidence == first.confidence
        assert res.notes == first.notes
