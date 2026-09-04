"""
test_suitability_engine.py -- A3 acceptance tests for suitability engine.
"""
import pytest
from app.decision_engine.suitability import score_suitability, Factor, SuitabilityResult

def test_score_suitability_determinism():
    farm_conditions = {
        "water_availability": True,
        "soil_type": "red laterite",
        "district": "Tumkur",
        "state": "Karnataka",
    }
    crop = {
        "water_requirement": "MEDIUM",
        "season": "Kharif",
    }
    suitability_row = {
        "soil_type": "red laterite",
        "suitability_base_score": 87.0,
    }
    
    first_res = score_suitability(farm_conditions, crop, suitability_row)
    for _ in range(100):
        res = score_suitability(farm_conditions, crop, suitability_row)
        assert res.score == first_res.score
        assert len(res.factors) == len(first_res.factors)
        assert res.confidence == first_res.confidence
        assert res.notes == first_res.notes

def test_score_suitability_high_water_no_water():
    farm_conditions = {
        "water_availability": False,
        "soil_type": "red laterite",
    }
    crop = {
        "water_requirement": "HIGH",
        "season": "Kharif",
    }
    suitability_row = {
        "soil_type": "red laterite",
        "suitability_base_score": 75.0,
    }
    
    res = score_suitability(farm_conditions, crop, suitability_row)
    
    water_factor = next(f for f in res.factors if f.name == "Water compatibility")
    assert water_factor.value == 75.0 * 0.2
    assert res.score < 75.0

def test_score_suitability_golden_demo_groundnut():
    farm_conditions = {
        "water_availability": True,
        "soil_type": "red laterite",
        "district": "Tumkur",
        "state": "Karnataka",
    }
    crop = {
        "water_requirement": "MEDIUM",
        "season": "Kharif",
    }
    suitability_row = {
        "soil_type": "red laterite",
        "suitability_base_score": 87.0,
    }
    
    res = score_suitability(farm_conditions, crop, suitability_row)
    assert res.score == 87
    assert res.confidence == "HIGH"
    assert len(res.notes) == 0

def test_score_suitability_missing_data():
    farm_conditions = {
        "water_availability": None,
        "soil_type": None,
    }
    crop = {
        "water_requirement": None,
        "season": None,
    }
    suitability_row = None
    
    res = score_suitability(farm_conditions, crop, suitability_row)
    assert res.score == 60
    assert res.confidence == "LOW"
    assert len(res.notes) > 0
    for factor in res.factors:
        assert factor.value == 60.0

def test_pure_function_no_db():
    farm_conditions = {"water_availability": True, "soil_type": "loam"}
    crop = {"water_requirement": "LOW", "season": "Rabi"}
    suitability_row = None
    
    res = score_suitability(farm_conditions, crop, suitability_row)
    assert isinstance(res, SuitabilityResult)
