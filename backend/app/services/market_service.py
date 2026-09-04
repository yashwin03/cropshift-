"""
market_service.py -- A5 data layer and business logic interface for Market entities.
"""
from __future__ import annotations

import math
from typing import Optional

from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.crop import Crop
from app.models.farm import Farm
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.crop_economics import CropEconomics
from app.decision_engine.market import score_market_engine


from app.utils.geo import haversine_distance


def get_best_market_for_crop(
    db: Session,
    farm_id: int,
    crop_id: int
) -> Optional[dict]:
    """
    Look up all available markets for a given crop, compute their scores,
    and return the best market's details and normalized market score.
    
    If no crop price data exists, returns estimated data without crashing.
    """
    farm: Optional[Farm] = db.get(Farm, farm_id)
    crop: Optional[Crop] = db.get(Crop, crop_id)
    if farm is None or crop is None:
        return None

    # Farm coordinates
    farm_lat: Optional[float] = None
    farm_lon: Optional[float] = None
    if farm.location is not None:
        try:
            point: Point = to_shape(farm.location)
            farm_lon = point.x
            farm_lat = point.y
        except Exception:
            pass

    # Reference Price from CropEconomics
    econ = (
        db.query(CropEconomics)
        .filter(CropEconomics.crop_id == crop_id, CropEconomics.region == farm.state)
        .first()
    )
    if econ is None:
        econ = (
            db.query(CropEconomics)
            .filter(CropEconomics.crop_id == crop_id)
            .first()
        )
    reference_price = econ.expected_price_per_unit if econ else None

    # Query all markets
    markets = db.query(Market).all()
    if not markets:
        return None

    candidates = []
    for m in markets:
        # Distance calculation via PostGIS with Haversine fallback
        distance_km: Optional[float] = None
        if farm.location is not None and m.location is not None:
            try:
                # ST_DistanceSphere returns distance in meters
                dist_m = db.query(func.ST_DistanceSphere(farm.location, m.location)).scalar()
                if dist_m is not None:
                    distance_km = float(dist_m) / 1000.0
            except Exception:
                # Fallback to python Haversine
                if farm_lat is not None and farm_lon is not None:
                    try:
                        m_point: Point = to_shape(m.location)
                        distance_km = haversine_distance(farm_lat, farm_lon, m_point.y, m_point.x)
                    except Exception:
                        pass

        # Market Price for this crop
        mp = (
            db.query(MarketPrice)
            .filter(MarketPrice.market_id == m.id, MarketPrice.crop_id == crop_id)
            .first()
        )

        if mp is not None:
            price = mp.price
            price_unit = mp.price_unit
            trend = mp.trend
            data_status = mp.data_status
            data_source = mp.data_source if mp.data_source else "Database Snapshot"
        else:
            # Missing price data -> ESTIMATED status
            price = None
            price_unit = econ.yield_unit if econ else "quintal"
            trend = "STABLE"
            data_status = "ESTIMATED"
            data_source = econ.data_source if econ else "Reference Economics Estimate"

        # Compute Market Score
        score_res = score_market_engine(
            current_price=price,
            reference_price=reference_price,
            trend=trend,
            distance_km=distance_km,
            data_status=data_status
        )

        # Market coordinates
        market_lat: Optional[float] = None
        market_lon: Optional[float] = None
        if m.location is not None:
            try:
                m_point: Point = to_shape(m.location)
                market_lon = m_point.x
                market_lat = m_point.y
            except Exception:
                pass

        market_location = None
        if market_lat is not None and market_lon is not None:
            market_location = {"latitude": market_lat, "longitude": market_lon}

        candidates.append({
            "crop_id": crop_id,
            "crop_name": crop.name,
            "price": price,
            "price_unit": price_unit,
            "market_name": m.name,
            "market_location": market_location,
            "distance_km": distance_km,
            "trend": trend,
            "market_score": score_res["market_score"],
            "data_status": data_status,
            "data_source": data_source
        })

    if not candidates:
        return None

    # Sort candidates: highest score first, then closest distance, then name alphabetically
    # To handle None distance_km gracefully in sorting, use a large default value
    candidates.sort(
        key=lambda x: (
            -x["market_score"],
            x["distance_km"] if x["distance_km"] is not None else 999999.0,
            x["market_name"]
        )
    )

    return candidates[0]
