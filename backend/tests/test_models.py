"""
test_models.py — A1: verifies all 10 SQLAlchemy model tables are registered
and that basic column introspection works. No live DB needed for this test.
"""
import pytest
from sqlalchemy import inspect

from app.database.base import Base
import app.models  # noqa: F401 — registers all models


EXPECTED_TABLES = {
    "farmer",
    "farm",
    "crop",
    "crop_economics",
    "crop_suitability",
    "market",
    "market_price",
    "subsidy",
    "recommendation",
    "risk_scenario",
}


def test_all_tables_registered():
    """All 10 A1 entities must be present in Base.metadata."""
    registered = set(Base.metadata.tables.keys())
    missing = EXPECTED_TABLES - registered
    assert missing == set(), f"Missing tables: {missing}"


def test_farmer_columns():
    table = Base.metadata.tables["farmer"]
    cols = {c.name for c in table.columns}
    assert {"id", "name", "phone", "language", "district", "state"}.issubset(cols)


def test_farm_columns():
    table = Base.metadata.tables["farm"]
    cols = {c.name for c in table.columns}
    assert {"id", "farmer_id", "land_area_acre", "water_availability",
            "soil_type", "district", "state", "current_crop_id"}.issubset(cols)


def test_crop_columns():
    table = Base.metadata.tables["crop"]
    cols = {c.name for c in table.columns}
    assert {"id", "name", "crop_type", "season", "duration_days",
            "water_requirement", "is_oilseed"}.issubset(cols)


def test_crop_economics_columns():
    table = Base.metadata.tables["crop_economics"]
    cols = {c.name for c in table.columns}
    assert {"id", "crop_id", "region", "expected_yield_per_acre",
            "production_cost_per_acre", "expected_price_per_unit",
            "data_status", "data_source"}.issubset(cols)


def test_market_price_columns():
    table = Base.metadata.tables["market_price"]
    cols = {c.name for c in table.columns}
    assert {"id", "market_id", "crop_id", "price", "price_date",
            "trend", "data_status"}.issubset(cols)


def test_recommendation_columns():
    table = Base.metadata.tables["recommendation"]
    cols = {c.name for c in table.columns}
    assert {"id", "farm_id", "recommended_crop_id", "suitability_score",
            "profitability_score", "market_score", "risk_score",
            "safety_score", "decision", "reasons", "risks"}.issubset(cols)


def test_risk_scenario_columns():
    table = Base.metadata.tables["risk_scenario"]
    cols = {c.name for c in table.columns}
    assert {"id", "code", "name", "price_multiplier",
            "yield_multiplier", "water_penalty"}.issubset(cols)


def test_subsidy_columns():
    table = Base.metadata.tables["subsidy"]
    cols = {c.name for c in table.columns}
    assert {"id", "scheme_id", "scheme_name", "applicable_crop_types",
            "eligibility_factors", "verification_required"}.issubset(cols)
