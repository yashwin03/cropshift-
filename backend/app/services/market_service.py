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


def get_crop_market_price_info(
    db: Session,
    crop_id: int,
    farm_id: Optional[int] = None
) -> Optional[dict]:
    """
    Retrieves current market price, price date, data status, data source,
    and recommended target price range for a crop.
    """
    crop = db.get(Crop, crop_id)
    if not crop:
        return None

    best_market = None
    if farm_id is not None:
        best_market = get_best_market_for_crop(db, farm_id, crop_id)

    price: Optional[float] = None
    market_name: str = "Regional Central APMC"
    data_status: str = "ESTIMATED"
    data_source: str = "Database Snapshot"
    price_date: Optional[str] = None

    if best_market and best_market.get("price") is not None:
        price = float(best_market["price"])
        market_name = best_market.get("market_name", "APMC Market")
        data_status = best_market.get("data_status", "LIVE")
        data_source = best_market.get("data_source", "Database Snapshot")

        mp_rec = (
            db.query(MarketPrice)
            .filter(MarketPrice.crop_id == crop_id)
            .order_by(MarketPrice.price_date.desc())
            .first()
        )
        if mp_rec and mp_rec.price_date:
            price_date = mp_rec.price_date.strftime("%d %b %Y")
    else:
        mp_rec = (
            db.query(MarketPrice)
            .filter(MarketPrice.crop_id == crop_id)
            .order_by(MarketPrice.price_date.desc())
            .first()
        )
        if mp_rec and mp_rec.price is not None:
            price = float(mp_rec.price)
            if mp_rec.market:
                market_name = mp_rec.market.name
            data_status = mp_rec.data_status or "STATIC"
            data_source = mp_rec.data_source or "Database Snapshot"
            if mp_rec.price_date:
                price_date = mp_rec.price_date.strftime("%d %b %Y")
        else:
            econ = db.query(CropEconomics).filter(CropEconomics.crop_id == crop_id).first()
            if econ and econ.expected_price_per_unit:
                price = float(econ.expected_price_per_unit)
                market_name = "Regional Central APMC"
                data_status = econ.data_status or "ESTIMATED"
                data_source = econ.data_source or "Reference Economics Estimate"
            else:
                return None

    # Calculate dynamic target price range (4% margin rounded to nearest 50, minimum 50)
    delta = max(50.0, round((price * 0.04) / 50.0) * 50.0)
    min_target_price = round(price - delta, 2)
    max_target_price = round(price + delta, 2)

    return {
        "crop_id": crop_id,
        "crop_name": crop.name,
        "price": price,
        "price_unit": "quintal",
        "min_target_price": min_target_price,
        "max_target_price": max_target_price,
        "price_date": price_date,
        "market_name": market_name,
        "data_status": data_status,
        "data_source": data_source,
    }


def validate_target_price_bounds(
    db: Session,
    crop_id: int,
    target_price: Optional[float],
    farm_id: Optional[int] = None
) -> None:
    """
    Validates target_price against the crop's dynamic market price bounds.
    Raises HTTPException(400) if out of bounds or if market price unavailable.
    """
    if target_price is None:
        return

    price_info = get_crop_market_price_info(db, crop_id, farm_id)
    if not price_info or price_info.get("min_target_price") is None or price_info.get("max_target_price") is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Market price unavailable. Target price cannot be validated."
        )

    min_p = price_info["min_target_price"]
    max_p = price_info["max_target_price"]

    if target_price < min_p or target_price > max_p:
        from fastapi import HTTPException, status
        min_fmt = f"{int(min_p):,}" if min_p.is_integer() else f"{min_p:,.2f}"
        max_fmt = f"{int(max_p):,}" if max_p.is_integer() else f"{max_p:,.2f}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target price must be between ₹{min_fmt} and ₹{max_fmt} per quintal based on today's market price."
        )


