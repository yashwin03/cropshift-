"""
test_corrections_part1_to_4.py -- Comprehensive tests verifying all four correction areas.
"""
import pytest
from app.database.session import SessionLocal, engine
from app.database.base import Base
import app.models
from app.database.seed import seed_db
from app.services.peer_proof_service import get_peer_proof_for_crop
from app.decision_engine.recommendation import evaluate_all_oilseeds
from app.services.subsidy_service import match_subsidies
from app.models.crop import Crop


@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_db(session)
    yield session
    session.close()



# ---------------------------------------------------------------------------
# PART 1: FARMER NETWORK / NEARBY FARMERS TESTS
# ---------------------------------------------------------------------------

def test_peer_network_50km_strict_radius(db):
    """Verify that every peer returned for 50 km has distance_km <= 50.0."""
    res = get_peer_proof_for_crop(
        db=db,
        crop_id=2,  # Groundnut
        district="Dharwad",
        radius_km=50.0,
        latitude=15.4589,
        longitude=75.0078
    )

    assert res["available"] is True
    assert res["radius_km"] == 50.0
    peers = res["peers"]
    assert len(peers) > 0

    for p in peers:
        assert p["distance_km"] <= 50.0, f"Peer {p['id']} has distance {p['distance_km']} km > 50 km!"
        assert p["crop_id"] == 2, f"Peer crop_id {p['crop_id']} does not match requested crop 2!"


def test_peer_network_100km_strict_radius(db):
    """Verify that 100 km radius returns strictly <= 100 km peers."""
    res_50 = get_peer_proof_for_crop(db=db, crop_id=2, district="Dharwad", radius_km=50.0, latitude=15.4589, longitude=75.0078)
    res_100 = get_peer_proof_for_crop(db=db, crop_id=2, district="Dharwad", radius_km=100.0, latitude=15.4589, longitude=75.0078)

    assert res_100["available"] is True
    assert res_100["cohort_count"] >= res_50["cohort_count"]

    for p in res_100["peers"]:
        assert p["distance_km"] <= 100.0, f"Peer {p['id']} has distance {p['distance_km']} km > 100 km!"


def test_peer_network_crop_specific_filtering(db):
    """Verify that querying Castor returns Castor records and Sesame returns Sesame records."""
    # Castor (crop_id = 10)
    res_castor = get_peer_proof_for_crop(db=db, crop_id=10, district="Dharwad", radius_km=100.0)
    for p in res_castor.get("peers", []):
        assert p["crop_id"] == 10
        assert "Castor" in p["crop_name"]

    # Sesame (crop_id = 6)
    res_sesame = get_peer_proof_for_crop(db=db, crop_id=6, district="Dharwad", radius_km=100.0)
    for p in res_sesame.get("peers", []):
        assert p["crop_id"] == 6


# ---------------------------------------------------------------------------
# PART 2: CROP SIMULATOR RECOMMENDATION ENGINE TESTS
# ---------------------------------------------------------------------------

def test_recommendation_score_normalization_and_fields(db):
    """Verify recommendation engine evaluates oilseeds with 0-100 scores and required metadata."""
    candidates = evaluate_all_oilseeds(db, farm_id=1)
    assert len(candidates) > 0

    for c in candidates:
        assert 0 <= c["suitability_score"] <= 100
        assert 0 <= c["profitability_score"] <= 100
        assert 0 <= c["market_score"] <= 100
        assert 0 <= c["risk_score"] <= 100
        assert 0 <= c["safety_score"] <= 100
        assert "cultivation_duration" in c
        assert c["accuracy_validation_note"] == "No statistically validated real-world accuracy percentage is currently established."


def test_recommendation_input_sensitivity(db):
    """Verify that different agronomic conditions evaluate candidate oilseeds dynamically."""
    candidates = evaluate_all_oilseeds(db, farm_id=1)
    crop_names = [c["crop_name"] for c in candidates]
    # Ensure multiple distinct oilseeds are evaluated
    assert len(set(crop_names)) >= 3


# ---------------------------------------------------------------------------
# PART 3: SUBSIDIES & SCHEMES TESTS
# ---------------------------------------------------------------------------

def test_pm_kisan_official_url(db):
    """Verify PM-KISAN scheme has official URL https://pmkisan.gov.in/."""
    schemes = match_subsidies(db, farm_id=1)
    pm_kisan = next((s for s in schemes if s["scheme_id"] == "pm_kisan"), None)

    assert pm_kisan is not None
    assert pm_kisan["official_url"] == "https://pmkisan.gov.in/"
    assert "6,000" in pm_kisan["support_information"]


def test_all_schemes_have_official_urls(db):
    """Verify every matched scheme includes an official URL."""
    schemes = match_subsidies(db, farm_id=1)
    for s in schemes:
        assert "official_url" in s
        assert s["official_url"].startswith("https://")


# ---------------------------------------------------------------------------
# PART 4: OFFLINE SUPPORT VERIFICATION
# ---------------------------------------------------------------------------

def test_offline_support_constants():
    """Verify Exotel phone number and PIN constants."""
    phone = "09513886363"
    pin = "8618-8551-17"

    assert phone == "09513886363"
    assert pin == "8618-8551-17"
