"""
test_profitability_engine.py -- A4 acceptance tests for profitability engine.
"""
import pytest
from app.decision_engine.profitability import calculate_profitability, ProfitabilityResult

def test_profitability_golden_demo():
    farm_conditions = {
        "district": "Tumkur",
        "state": "Karnataka"
    }
    
    # Paddy economics (Current crop)
    # expected_yield = 20.0 quintals, cost = 18,000, price = 2,500
    # Expected revenue = 20 * 2500 = 50,000
    # Expected profit = 50000 - 18000 = 32,000
    current_crop_econ = {
        "expected_yield_per_acre": 20.0,
        "yield_unit": "quintal",
        "production_cost_per_acre": 18000.0,
        "expected_price_per_unit": 2500.0,
        "data_source": "Karnataka Dept of Agriculture",
        "data_status": "STATIC"
    }
    
    # Groundnut economics (Alternative crop)
    # expected_yield = 10.0 quintals, cost = 12,000, price = 5,500
    # Expected revenue = 10 * 5500 = 55,000
    # Expected profit = 55000 - 12000 = 43,000
    alternative_crop_econ = {
        "expected_yield_per_acre": 10.0,
        "yield_unit": "quintal",
        "production_cost_per_acre": 12000.0,
        "expected_price_per_unit": 5500.0,
        "data_source": "Karnataka Dept of Agriculture",
        "data_status": "STATIC"
    }
    
    res = calculate_profitability(
        farm_conditions=farm_conditions,
        current_crop_econ=current_crop_econ,
        alternative_crop_econ=alternative_crop_econ,
        land_area_acre=1.0
    )
    
    assert res.current_crop_profit == 32000
    assert res.estimated_profit == 43000
    assert res.profit_difference == 11000
    assert res.profitability_score == 84
    assert "disclaimer" in res.__dict__
    assert res.disclaimer == "Estimated figures based on Karnataka Dept of Agriculture. Actual results vary."
    assert len(res.assumptions) > 0
    assert any("Region: Tumkur" in a for a in res.assumptions)

def test_profitability_zero_yield_and_cost():
    farm_conditions = {}
    current_crop_econ = {
        "expected_yield_per_acre": 0.0,
        "production_cost_per_acre": 0.0,
        "expected_price_per_unit": 0.0
    }
    alternative_crop_econ = {
        "expected_yield_per_acre": 0.0,
        "production_cost_per_acre": 0.0,
        "expected_price_per_unit": 0.0
    }
    
    res = calculate_profitability(farm_conditions, current_crop_econ, alternative_crop_econ)
    assert res.current_crop_profit == 0
    assert res.estimated_profit == 0
    assert res.profit_difference == 0
    assert res.profitability_score == 50  # 50 + 0 = 50

def test_profitability_negative_profits():
    farm_conditions = {}
    
    # Current crop profit = 10 * 50 - 10000 = -9500
    current_crop_econ = {
        "expected_yield_per_acre": 10.0,
        "production_cost_per_acre": 10000.0,
        "expected_price_per_unit": 50.0
    }
    
    # Alternative crop profit = 10 * 80 - 10000 = -9200 (alternative is better by 300)
    alternative_crop_econ = {
        "expected_yield_per_acre": 10.0,
        "production_cost_per_acre": 10000.0,
        "expected_price_per_unit": 80.0
    }
    
    res = calculate_profitability(farm_conditions, current_crop_econ, alternative_crop_econ)
    assert res.current_crop_profit == -9500
    assert res.estimated_profit == -9200
    assert res.profit_difference == 300
    
    # ratio = 300 / max(-9500, 1.0) = 300 / 1.0 = 300
    # score = clamp(round(50 + 300 * 100), 0, 100) = 100
    assert res.profitability_score == 100

def test_profitability_determinism():
    farm_conditions = {"district": "Haveri"}
    current_crop_econ = {
        "expected_yield_per_acre": 20.0,
        "production_cost_per_acre": 15000.0,
        "expected_price_per_unit": 1000.0
    }
    alternative_crop_econ = {
        "expected_yield_per_acre": 15.0,
        "production_cost_per_acre": 10000.0,
        "expected_price_per_unit": 2000.0
    }
    
    first = calculate_profitability(farm_conditions, current_crop_econ, alternative_crop_econ)
    for _ in range(100):
        res = calculate_profitability(farm_conditions, current_crop_econ, alternative_crop_econ)
        assert res.profitability_score == first.profitability_score
        assert res.estimated_profit == first.estimated_profit
        assert res.current_crop_profit == first.current_crop_profit
