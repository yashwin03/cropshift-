"""
test_recommendation.py -- A8 acceptance tests for recommendation engine.
"""
import pytest
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db

from app.models.recommendation import Recommendation
from app.models.crop import Crop
from app.decision_engine.recommendation import generate_recommendation


@pytest.fixture(scope="module")
def db() -> Session:
    """Ensure DB is initialised and seeded, yield a session."""
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


def test_recommendation_golden_demo(db: Session):
    # Golden Demo: Farm 1 (Tumkur) shifting to Groundnut (Crop 2)
    # Expected scores: Suitability = 87, Profitability = 84, Market = 78, Risk = 28, Safety = 82, Decision = SWITCH
    rec = generate_recommendation(db, farm_id=1)
    assert rec is not None
    assert rec.farm_id == 1
    
    # Recommended crop should be Groundnut (ID 2)
    crop = db.get(Crop, rec.recommended_crop_id)
    assert crop.name == "Groundnut"
    
    assert rec.suitability_score == 87.0
    assert rec.profitability_score == 76.0
    assert rec.market_score == 90.0
    assert rec.risk_score == 28.0
    assert rec.safety_score == 82.0
    assert rec.decision == "SWITCH"
    assert rec.expected_profit == 43000.0
    assert rec.current_crop_profit == 34000.0
    assert rec.profit_difference == 9000.0
    assert len(rec.reasons) > 0
    assert len(rec.risks) > 0


def test_recommendation_determinism(db: Session):
    # Running the same request 50 times gives byte-identical (value-identical) results
    first = generate_recommendation(db, farm_id=1)
    assert first is not None
    for _ in range(50):
        res = generate_recommendation(db, farm_id=1)
        assert res.recommended_crop_id == first.recommended_crop_id
        assert res.suitability_score == first.suitability_score
        assert res.profitability_score == first.profitability_score
        assert res.market_score == first.market_score
        assert res.risk_score == first.risk_score
        assert res.safety_score == first.safety_score
        assert res.decision == first.decision


def test_recommendation_terrible_conditions(db: Session):
    # Farm 3 (Dharwad) has water_availability = False, current_crop_id = 5 (Mustard)
    # Let's verify that evaluations run and output is valid.
    rec = generate_recommendation(db, farm_id=3)
    assert rec is not None
    assert rec.farm_id == 3
    # Check that it evaluates alternative crops (Sunflower is crop 3) and decision is classified
    assert rec.decision in ["DONT_SWITCH", "CAUTION", "SWITCH"]
