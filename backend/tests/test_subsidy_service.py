"""
test_subsidy_service.py -- A10 acceptance tests for Subsidy Matcher.
"""
import pytest
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db

from app.services.subsidy_service import match_subsidies


@pytest.fixture(scope="module")
def db() -> Session:
    """Ensure DB is initialised and seeded, yield a session."""
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


def test_subsidy_fields_and_types(db: Session):
    # Match subsidies with default arguments
    schemes = match_subsidies(db, farm_id=1)
    assert len(schemes) == 5
    
    required_keys = {
        "scheme_id", "scheme_name", "relevance", "eligibility_status",
        "eligibility_factors", "required_information", "support_information",
        "verification_required", "data_source"
    }

    for s in schemes:
        # Check all 9 fields exist exactly
        assert set(s.keys()) == required_keys
        
        # Check field types and enums
        assert isinstance(s["scheme_id"], str)
        assert isinstance(s["scheme_name"], str)
        assert s["relevance"] in {"HIGH", "MEDIUM", "LOW"}
        assert s["eligibility_status"] in {"LIKELY_ELIGIBLE", "VERIFICATION_REQUIRED", "LIKELY_NOT_ELIGIBLE"}
        assert isinstance(s["eligibility_factors"], list)
        assert isinstance(s["required_information"], list)
        assert isinstance(s["support_information"], str)
        assert isinstance(s["verification_required"], bool)
        assert isinstance(s["data_source"], str)
        assert s["data_source"] != ""


def test_subsidy_unknown_landholding_proof(db: Session):
    # If has_land_proof is False/unknown, schemes requiring land proof (like NMEO-OS, PM-KISAN, PMFBY)
    # must return VERIFICATION_REQUIRED and verification_required = True
    schemes = match_subsidies(db, farm_id=1, has_land_proof=False)
    
    for s in schemes:
        if s["scheme_id"] in ["nmeo_os", "pm_kisan", "pmfby", "state_oilseed_support"]:
            assert s["eligibility_status"] == "VERIFICATION_REQUIRED"
            assert s["verification_required"] is True


def test_subsidy_oilseed_relevance_high(db: Session):
    # Under Groundnut recommendation (ID 2), NMEO-OS relevance must be HIGH
    schemes = match_subsidies(db, farm_id=1, recommended_crop_id=2)
    nmeo = next(s for s in schemes if s["scheme_id"] == "nmeo_os")
    assert nmeo["relevance"] == "HIGH"


def test_subsidy_no_fabricated_eligibility(db: Session):
    # No scheme should be LIKELY_ELIGIBLE unless all checklist factors are satisfied.
    # For NMEO-OS, it requires land proof AND recommended crop must be an oilseed.
    # If recommended crop is not an oilseed (Paddy, ID 1), it shouldn't be LIKELY_ELIGIBLE even with land proof.
    schemes = match_subsidies(db, farm_id=1, has_land_proof=True, recommended_crop_id=1)
    nmeo = next(s for s in schemes if s["scheme_id"] == "nmeo_os")
    assert nmeo["eligibility_status"] == "LIKELY_NOT_ELIGIBLE"

    # Soil Health Card scheme needs has_soil_health_card = True to be LIKELY_ELIGIBLE
    schemes_no_shc = match_subsidies(db, farm_id=1, has_soil_health_card=False)
    shc_no = next(s for s in schemes_no_shc if s["scheme_id"] == "soil_health_card")
    assert shc_no["eligibility_status"] == "VERIFICATION_REQUIRED"
    assert shc_no["verification_required"] is True

    schemes_shc = match_subsidies(db, farm_id=1, has_soil_health_card=True)
    shc_yes = next(s for s in schemes_shc if s["scheme_id"] == "soil_health_card")
    assert shc_yes["eligibility_status"] == "LIKELY_ELIGIBLE"
    assert shc_yes["verification_required"] is True or shc_yes["verification_required"] is False
