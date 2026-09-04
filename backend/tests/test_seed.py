"""
test_seed.py — A1: integration tests against the live cropshift DB.
Requires PostgreSQL running with DATABASE_URL configured.

Tests:
1. Tables create without error.
2. Seed runs successfully.
3. Seed is idempotent — running twice yields identical row counts.
4. Golden demo farm (id=1, Paddy, 1 acre, water available) exists and is correct.
5. Farm 1 can be retrieved with farmer and current crop.
"""
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import engine, SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db
from app.models import (
    Farmer, Farm, Crop, CropEconomics, CropSuitability,
    Market, MarketPrice, Subsidy, RiskScenario, RiskCode,
)


@pytest.fixture(scope="module")
def db_session():
    """Create tables, seed once, then yield a session. Tear down after module."""
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


def _count(session: Session, model) -> int:
    return session.query(model).count()


# ---------------------------------------------------------------------------
# Table creation
# ---------------------------------------------------------------------------

def test_postgis_extension(db_session: Session):
    result = db_session.execute(text("SELECT postgis_version();")).fetchone()
    assert result is not None, "PostGIS extension must be installed"


def test_all_tables_exist(db_session: Session):
    result = db_session.execute(text(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public';"
    )).fetchall()
    tables = {r[0] for r in result}
    for expected in [
        "farmer", "farm", "crop", "crop_economics", "crop_suitability",
        "market", "market_price", "subsidy", "recommendation", "risk_scenario",
    ]:
        assert expected in tables, f"Table '{expected}' not found in database"


# ---------------------------------------------------------------------------
# Seed counts
# ---------------------------------------------------------------------------

def test_seed_crop_count(db_session: Session):
    assert _count(db_session, Crop) >= 7, "Must have at least 7 crops"


def test_seed_farmer_count(db_session: Session):
    assert _count(db_session, Farmer) >= 3, "Must have at least 3 farmers"


def test_seed_farm_count(db_session: Session):
    assert _count(db_session, Farm) >= 3, "Must have at least 3 farms"


def test_seed_market_count(db_session: Session):
    assert _count(db_session, Market) >= 4, "Must have at least 4 markets"


def test_seed_risk_scenario_count(db_session: Session):
    assert _count(db_session, RiskScenario) == 4, "Must have exactly 4 risk scenarios"


def test_seed_subsidy_count(db_session: Session):
    assert _count(db_session, Subsidy) >= 4, "Must have at least 4 subsidies"


def test_seed_crop_economics_count(db_session: Session):
    assert _count(db_session, CropEconomics) >= 7, "Must have economics for every crop"


def test_seed_market_price_count(db_session: Session):
    count = _count(db_session, MarketPrice)
    assert count >= 14, f"Must have market prices for every crop in ≥2 markets, got {count}"


# ---------------------------------------------------------------------------
# Idempotency: run seed again, counts must not change
# ---------------------------------------------------------------------------

def test_seed_idempotent(db_session: Session):
    counts_before = {
        "crop":    _count(db_session, Crop),
        "farmer":  _count(db_session, Farmer),
        "farm":    _count(db_session, Farm),
        "market":  _count(db_session, Market),
        "subsidy": _count(db_session, Subsidy),
    }
    seed_db(db_session)   # second run
    for table, before in counts_before.items():
        after = _count(db_session, eval(table.capitalize()))
        assert after == before, (
            f"Idempotency broken for '{table}': {before} → {after}"
        )


# ---------------------------------------------------------------------------
# Golden demo farm (id=1) — Section 15
# ---------------------------------------------------------------------------

def test_golden_demo_farm_exists(db_session: Session):
    farm = db_session.get(Farm, 1)
    assert farm is not None, "Farm id=1 (golden demo farm) must exist"


def test_golden_demo_farm_land_area(db_session: Session):
    farm = db_session.get(Farm, 1)
    assert farm.land_area_acre == pytest.approx(1.0), "Golden demo farm must be 1 acre"


def test_golden_demo_farm_water_available(db_session: Session):
    farm = db_session.get(Farm, 1)
    assert farm.water_availability is True, "Golden demo farm must have water available"


def test_golden_demo_farm_current_crop_is_paddy(db_session: Session):
    farm = db_session.get(Farm, 1)
    assert farm.current_crop is not None, "Golden demo farm must have a current crop"
    assert farm.current_crop.name == "Paddy", (
        f"Golden demo farm current crop must be Paddy, got {farm.current_crop.name}"
    )


def test_golden_demo_farm_farmer_linked(db_session: Session):
    farm = db_session.get(Farm, 1)
    assert farm.farmer is not None, "Farm 1 must have a linked farmer"
    assert farm.farmer.id == farm.farmer_id


# ---------------------------------------------------------------------------
# Risk scenario codes
# ---------------------------------------------------------------------------

def test_risk_scenario_codes(db_session: Session):
    codes = {r.code for r in db_session.query(RiskScenario).all()}
    for required in [RiskCode.BASELINE, RiskCode.PRICE_DOWN,
                     RiskCode.YIELD_DOWN, RiskCode.WATER_RISK]:
        assert required in codes, f"Risk code {required} missing"
