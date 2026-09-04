"""
test_geospatial.py -- A11 acceptance tests for Geospatial Intelligence.
"""
import pytest
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.database.init_db import init_db
from app.database.seed import seed_db

from app.models.farm import Farm
from app.geospatial.service import (
    get_farm_location,
    distance_km,
    get_nearby_markets,
    get_geographic_context
)


@pytest.fixture(scope="module")
def db() -> Session:
    """Ensure DB is initialised and seeded, yield a session."""
    init_db()
    with SessionLocal() as session:
        seed_db(session)
        yield session


def test_get_farm_location(db: Session):
    # Farm 1 is seeded with coordinates around Tumkur (13.3409, 77.1025)
    loc = get_farm_location(db, 1)
    assert loc is not None
    assert "latitude" in loc
    assert "longitude" in loc
    assert loc["latitude"] == pytest.approx(13.3409, abs=0.01)
    assert loc["longitude"] == pytest.approx(77.1025, abs=0.01)


def test_distance_km():
    # distance between Tumkur (13.3409, 77.1025) and Bangalore (12.9716, 77.5946)
    # expected to be ~67.3 km
    pt_a_tuple = (13.3409, 77.1025)
    pt_b_tuple = (12.9716, 77.5946)
    assert distance_km(pt_a_tuple, pt_b_tuple) == pytest.approx(67.3, abs=0.5)

    pt_a_dict = {"latitude": 13.3409, "longitude": 77.1025}
    pt_b_dict = {"lat": 12.9716, "lon": 77.5946}
    assert distance_km(pt_a_dict, pt_b_dict) == pytest.approx(67.3, abs=0.5)


def test_get_nearby_markets_ascending(db: Session):
    # Farm 1 has coordinates. Markets should be returned sorted by distance ascending.
    res = get_nearby_markets(db, farm_id=1, radius_km=200.0, limit=5)
    assert res["note"] is None
    markets = res["markets"]
    assert len(markets) >= 1
    
    # Assert sorted ascending
    distances = [m["distance_km"] for m in markets]
    assert distances == sorted(distances)


def test_get_nearby_markets_null_geometry(db: Session):
    # Insert a temporary farm with NULL location geometry
    temp_farm = Farm(
        id=9999,
        farmer_id=1,
        land_area_acre=2.5,
        water_availability=True,
        soil_type="red laterite",
        district="Tumkur",
        state="Karnataka",
        current_crop_id=1
    )
    db.add(temp_farm)
    db.commit()
    db.refresh(temp_farm)

    try:
        # Query nearby markets for NULL location farm
        res = get_nearby_markets(db, farm_id=temp_farm.id)
        assert res["markets"] == []
        assert "no location" in res["note"].lower() or "missing" in res["note"].lower()
    finally:
        # Cleanup
        db.delete(temp_farm)
        db.commit()


def test_get_geographic_context(db: Session):
    context = get_geographic_context(db, farm_id=1)
    assert context is not None
    assert context["district"] == "Tumkur"
    assert context["state"] == "Karnataka"
    assert "agro_climatic_zone" in context
    assert context["agro_climatic_zone"] is None  # Zone not seeded
    assert isinstance(context["nearby_market_count"], int)
    assert context["nearby_market_count"] >= 1
