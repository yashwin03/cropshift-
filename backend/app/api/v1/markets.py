from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

from app.database.session import get_db
from app.models.crop import Crop
from app.models.crop_economics import CropEconomics
from app.services.market_service import get_best_market_for_crop
from app.schemas.market import MarketResponse

router = APIRouter()

@router.get("/{crop_id}", response_model=MarketResponse)
def get_market_info(
    crop_id: int,
    farm_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    crop = db.get(Crop, crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail="Crop not found.")

    # Fetch crop economics
    econ = db.query(CropEconomics).filter(CropEconomics.crop_id == crop_id).first()

    if farm_id is not None:
        m_res = get_best_market_for_crop(db, farm_id, crop_id)
        if m_res:
            return MarketResponse(
                crop_id=crop_id,
                crop_name=crop.name,
                price=float(m_res["price"]) if m_res["price"] is not None else None,
                price_unit=m_res["price_unit"],
                market_name=m_res["market_name"],
                market_location=m_res["market_location"],
                distance_km=float(m_res["distance_km"]) if m_res["distance_km"] is not None else None,
                trend=m_res["trend"],
                market_score=int(m_res["market_score"]),
                data_status=m_res["data_status"],
                data_source=m_res["data_source"]
            )

    # Fallback/Default if farm_id not provided or market not found
    price_val = float(econ.expected_price_per_unit) if econ else None
    unit_val = econ.yield_unit if econ else "quintal"
    status_val = econ.data_status if econ else "ESTIMATED"
    source_val = econ.data_source if (econ and econ.data_source) else "Database Snapshot"

    return MarketResponse(
        crop_id=crop_id,
        crop_name=crop.name,
        price=price_val,
        price_unit=unit_val,
        market_name="Regional Central APMC",
        market_location=None,
        distance_km=None,
        trend="STABLE",
        market_score=60,
        data_status=status_val,
        data_source=source_val
    )
