"""
test_market_service.py -- A5 acceptance tests for market intelligence engine/service.
"""
import pytest
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db

from app.decision_engine.market import score_market_engine
from app.services.market_service import get_best_market_for_crop, haversine_distance


@pytest.fixture(scope="module")
def db() -> Session:
    """Ensure DB is initialised and seeded, yield a session."""
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


def test_score_market_engine_bounds():
    res = score_market_engine(
        current_price=10000.0,
        reference_price=100.0,
        trend="RISING",
        distance_km=0.0,
        data_status="REAL"
    )
    assert res["market_score"] == 96

    res = score_market_engine(
        current_price=0.0,
        reference_price=100.0,
        trend="FALLING",
        distance_km=500.0,
        data_status="DEMO"
    )
    assert 0 <= res["market_score"] <= 100


def test_trend_impact_on_score():
    rising = score_market_engine(
        current_price=100.0,
        reference_price=100.0,
        trend="RISING",
        distance_km=10.0,
        data_status="REAL"
    )
    falling = score_market_engine(
        current_price=100.0,
        reference_price=100.0,
        trend="FALLING",
        distance_km=10.0,
        data_status="REAL"
    )
    assert falling["market_score"] < rising["market_score"]


def test_missing_price_fallback():
    res = score_market_engine(
        current_price=None,
        reference_price=100.0,
        trend="STABLE",
        distance_km=10.0,
        data_status="ESTIMATED"
    )
    assert 0 <= res["market_score"] <= 100
    assert res["price_score"] == 60.0


def test_distance_haversine():
    # Tumkur (13.3409, 77.1025) to Bengaluru (12.9716, 77.5946)
    dist = haversine_distance(13.3409, 77.1025, 12.9716, 77.5946)
    assert 60.0 <= dist <= 80.0


def test_get_best_market_for_crop_golden_demo(db: Session):
    # Farm 1 (Tumkur) + Crop 2 (Groundnut)
    res = get_best_market_for_crop(db, farm_id=1, crop_id=2)
    assert res is not None
    assert res["crop_id"] == 2
    assert res["crop_name"] == "Groundnut"
    assert res["market_name"] == "Tumkur APMC"
    assert res["trend"] == "RISING"
    assert res["data_status"] == "DEMO"
    assert res["market_score"] > 0
    assert "market_location" in res
    assert res["market_location"] is not None


def test_get_best_market_missing_price_db(db: Session):
    from app.models import MarketPrice
    db.query(MarketPrice).filter(MarketPrice.crop_id == 7).delete()
    db.commit()

    res = get_best_market_for_crop(db, farm_id=1, crop_id=7)
    assert res is not None
    assert res["crop_id"] == 7
    assert res["data_status"] == "ESTIMATED"
    assert res["price"] is None
    assert res["market_score"] > 0
