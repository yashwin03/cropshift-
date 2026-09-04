"""
crop_service.py -- A2 data layer for Crop entities.

Responsibilities:
- Look up individual crops, list all crops, and find candidate alternative
  crops for the shift evaluation.
- Return plain dicts (never raw ORM objects).
- Filter alternative crops to oilseeds only, excluding the current crop.

Business logic lives in decision_engine/. This module is pure data access.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.farm import Farm
from app.models.crop_economics import CropEconomics
from app.models.crop_suitability import CropSuitability


# ---------------------------------------------------------------------------
# Single-crop lookups
# ---------------------------------------------------------------------------

def get_crop(db: Session, crop_id: int) -> Optional[dict]:
    """Return a plain dict for the requested crop, or None if not found."""
    crop: Optional[Crop] = db.get(Crop, crop_id)
    if crop is None:
        return None
    return _crop_to_dict(crop)


def list_crops(db: Session) -> list[dict]:
    """Return all crops as plain dicts."""
    crops = db.query(Crop).order_by(Crop.id).all()
    return [_crop_to_dict(c) for c in crops]


def get_current_crop(db: Session, farm_id: int) -> Optional[dict]:
    """Return the current crop of the specified farm, or None."""
    farm: Optional[Farm] = db.get(Farm, farm_id)
    if farm is None or farm.current_crop is None:
        return None
    return _crop_to_dict(farm.current_crop)


def get_alternative_crops(db: Session, farm_id: int) -> list[dict]:
    """Return candidate oilseed crops for shift evaluation.

    Rules per spec:
    - Only oilseed crops (is_oilseed == True).
    - The farm's current crop is excluded.
    - Results ordered by crop id (deterministic).
    """
    farm: Optional[Farm] = db.get(Farm, farm_id)
    if farm is None:
        return []

    current_crop_id: Optional[int] = farm.current_crop_id

    query = (
        db.query(Crop)
        .filter(Crop.is_oilseed == True)  # noqa: E712 -- SQLAlchemy requires ==
        .order_by(Crop.id)
    )
    if current_crop_id is not None:
        query = query.filter(Crop.id != current_crop_id)

    crops = query.all()
    return [_crop_to_dict(c) for c in crops]


def get_crop_requirements(db: Session, crop_id: int) -> Optional[dict]:
    """Return water requirement, soil preference, and season for a crop.

    This is the subset of crop attributes the suitability engine cares about.
    Returns None if crop not found.
    """
    crop: Optional[Crop] = db.get(Crop, crop_id)
    if crop is None:
        return None

    # Fetch the first matching suitability row if available
    suitability = (
        db.query(CropSuitability)
        .filter(CropSuitability.crop_id == crop_id)
        .first()
    )
    preferred_soil = suitability.soil_type if suitability else None

    return {
        "crop_id": crop.id,
        "crop_name": crop.name,
        "water_requirement": crop.water_requirement,   # HIGH / MEDIUM / LOW
        "preferred_soil": preferred_soil,              # may be None
        "season": crop.season,
        "duration_days": crop.duration_days,
    }


def get_crop_economics(db: Session, crop_id: int, region: str = "Karnataka") -> Optional[dict]:
    """Return economics row for a crop in the specified region.

    Falls back to the first available row if the exact region is not found.
    Returns None if no economics row exists for this crop at all.
    """
    # Try exact region match first
    row: Optional[CropEconomics] = (
        db.query(CropEconomics)
        .filter(CropEconomics.crop_id == crop_id, CropEconomics.region == region)
        .first()
    )
    # Fallback: any region
    if row is None:
        row = (
            db.query(CropEconomics)
            .filter(CropEconomics.crop_id == crop_id)
            .first()
        )
    if row is None:
        return None
    return {
        "crop_id": row.crop_id,
        "region": row.region,
        "expected_yield_per_acre": row.expected_yield_per_acre,
        "yield_unit": row.yield_unit,
        "production_cost_per_acre": row.production_cost_per_acre,
        "expected_price_per_unit": row.expected_price_per_unit,
        "data_status": row.data_status,
        "data_source": row.data_source,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _crop_to_dict(crop: Crop) -> dict:
    """Convert a Crop ORM object to a plain dict."""
    return {
        "id": crop.id,
        "name": crop.name,
        "crop_type": crop.crop_type,
        "is_oilseed": crop.is_oilseed,
        "season": crop.season,
        "duration_days": crop.duration_days,
        "water_requirement": crop.water_requirement,
    }
