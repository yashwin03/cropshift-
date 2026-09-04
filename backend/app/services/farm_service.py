"""
farm_service.py -- A2 data layer for Farmer and Farm entities.

Responsibilities:
- Look up farmers, farms, and farm conditions from the database.
- Return plain dicts (never raw ORM objects) to keep the decision engine
  decoupled from SQLAlchemy internals.
- Handle missing geometry, missing soil type, and missing current crop
  gracefully -- never raise, always explain.

Business logic lives in decision_engine/. This module is pure data access.
"""
from __future__ import annotations

from typing import Optional

from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from sqlalchemy.orm import Session

from app.models.farm import Farm
from app.models.farmer import Farmer


# ---------------------------------------------------------------------------
# Farmer lookups
# ---------------------------------------------------------------------------

def get_farmer(db: Session, farmer_id: int) -> Optional[dict]:
    """Return a plain dict for the requested farmer, or None if not found."""
    farmer: Optional[Farmer] = db.get(Farmer, farmer_id)
    if farmer is None:
        return None
    return {
        "id": farmer.id,
        "name": farmer.name,
        "phone": farmer.phone,
        "language": farmer.language,
        "district": farmer.district,
        "state": farmer.state,
    }


# ---------------------------------------------------------------------------
# Farm lookups
# ---------------------------------------------------------------------------

def get_farm(db: Session, farm_id: int) -> Optional[dict]:
    """Return a plain dict for the requested farm, or None if not found."""
    farm: Optional[Farm] = db.get(Farm, farm_id)
    if farm is None:
        return None
    return _farm_to_dict(farm)


def get_farm_by_farmer(db: Session, farmer_id: int) -> list[dict]:
    """Return all farms belonging to a farmer as a list of plain dicts."""
    farms = db.query(Farm).filter(Farm.farmer_id == farmer_id).all()
    return [_farm_to_dict(f) for f in farms]


# ---------------------------------------------------------------------------
# Farm conditions -- the normalised dict consumed by the decision engine
# ---------------------------------------------------------------------------

def get_farm_conditions(db: Session, farm_id: int) -> Optional[dict]:
    """Return normalised farm conditions for the decision engine.

    Keys returned:
        land_area_acre      float
        water_availability  bool
        soil_type           str | None   (None allowed; engine defaults)
        district            str | None
        state               str | None
        latitude            float | None
        longitude           float | None
        current_crop        dict | None  (id, name, crop_type, is_oilseed,
                                          water_requirement, season)
        _missing_geometry   bool         True if location was NULL
    """
    farm: Optional[Farm] = db.get(Farm, farm_id)
    if farm is None:
        return None

    # Extract coordinates from PostGIS geometry (may be NULL)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    missing_geometry = True

    if farm.location is not None:
        try:
            point: Point = to_shape(farm.location)
            longitude = point.x
            latitude = point.y
            missing_geometry = False
        except Exception:
            # Malformed geometry -- degrade gracefully
            pass

    # Current crop details (may be NULL)
    current_crop: Optional[dict] = None
    if farm.current_crop is not None:
        c = farm.current_crop
        current_crop = {
            "id": c.id,
            "name": c.name,
            "crop_type": c.crop_type,
            "is_oilseed": c.is_oilseed,
            "water_requirement": c.water_requirement,
            "season": c.season,
            "duration_days": c.duration_days,
        }

    return {
        "farm_id": farm.id,
        "farmer_id": farm.farmer_id,
        "land_area_acre": farm.land_area_acre,
        "water_availability": farm.water_availability,
        "soil_type": farm.soil_type,           # None is valid
        "district": farm.district,
        "state": farm.state,
        "latitude": latitude,
        "longitude": longitude,
        "current_crop": current_crop,
        "_missing_geometry": missing_geometry,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _farm_to_dict(farm: Farm) -> dict:
    """Convert a Farm ORM object to a plain dict."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    if farm.location is not None:
        try:
            point: Point = to_shape(farm.location)
            longitude = point.x
            latitude = point.y
        except Exception:
            pass

    return {
        "id": farm.id,
        "farmer_id": farm.farmer_id,
        "land_area_acre": farm.land_area_acre,
        "water_availability": farm.water_availability,
        "soil_type": farm.soil_type,
        "district": farm.district,
        "state": farm.state,
        "latitude": latitude,
        "longitude": longitude,
        "current_crop_id": farm.current_crop_id,
    }
