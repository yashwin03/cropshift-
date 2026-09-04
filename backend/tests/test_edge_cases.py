"""
test_edge_cases.py -- A15 Edge Cases test suite.
"""
import pytest
from app.decision_engine.profitability import calculate_profitability
from app.utils.geo import haversine_distance
from app.geospatial.service import distance_km
from app.services.subsidy_service import match_subsidies
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db


@pytest.fixture(scope="module")
def db() -> Session:
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


def test_profitability_zero_land_area():
    farm_cond = {"district": "Tumkur", "state": "Karnataka"}
    curr_econ = {
        "expected_yield_per_acre": 20.0,
        "production_cost_per_acre": 18000,
        "expected_price_per_unit": 2600,
        "data_status": "DEMO"
    }
    alt_econ = {
        "expected_yield_per_acre": 10.0,
        "production_cost_per_acre": 12000,
        "expected_price_per_unit": 5500,
        "data_status": "DEMO"
    }
    
    # Run calculation with 0.0 acres
    res = calculate_profitability(farm_cond, curr_econ, alt_econ, land_area_acre=0.0)
    assert res.profitability_score == 76  # Ratio stays identical because score normalization is per-acre ratio
    assert res.expected_yield == 10.0


def test_profitability_negative_profit():
    farm_cond = {"district": "Tumkur", "state": "Karnataka"}
    # Cost is higher than revenue -> negative profit
    curr_econ = {
        "expected_yield_per_acre": 5.0,
        "production_cost_per_acre": 20000,
        "expected_price_per_unit": 2000,
        "data_status": "DEMO"
    }
    alt_econ = {
        "expected_yield_per_acre": 10.0,
        "production_cost_per_acre": 12000,
        "expected_price_per_unit": 5500,
        "data_status": "DEMO"
    }
    res = calculate_profitability(farm_cond, curr_econ, alt_econ, land_area_acre=1.0)
    assert res.current_crop_profit < 0
    assert res.profitability_score == 100  # High relative improvement


def test_distance_km_invalid_points():
    with pytest.raises(ValueError):
        distance_km("invalid", "invalid")


def test_match_subsidies_no_proofs(db: Session):
    # Retrieve matching subsidies with False flags
    schemes = match_subsidies(db, farm_id=1, has_land_proof=False, has_soil_health_card=False, recommended_crop_id=2)
    assert len(schemes) == 5
    # NMEO-OS should show verification required
    nmeo = next(s for s in schemes if s["scheme_id"] == "nmeo_os")
    assert nmeo["eligibility_status"] == "VERIFICATION_REQUIRED"
    assert nmeo["verification_required"] is True
