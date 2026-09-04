"""
Geospatial services engine for CropShift.
Provides PostGIS and Haversine distance calculations, nearest markets, and geographical context.
"""
from sqlalchemy.orm import Session
from sqlalchemy import cast, func
from geoalchemy2 import Geography
from geoalchemy2.shape import to_shape
from shapely.geometry import Point
from typing import Dict, Any, List, Optional

from app.models.farm import Farm
from app.models.market import Market
from app.models.market_price import MarketPrice
from app.models.crop import Crop
from app.utils.geo import haversine_distance


def get_farm_location(db: Session, farm_id: int) -> Optional[Dict[str, float]]:
    """Retrieve farm coordinates as WGS84 floats."""
    farm = db.get(Farm, farm_id)
    if not farm or farm.location is None:
        return None
    try:
        point: Point = to_shape(farm.location)
        return {"latitude": float(point.y), "longitude": float(point.x)}
    except Exception:
        return None


def distance_km(point_a: Any, point_b: Any) -> float:
    """
    Calculate distance in km between point_a and point_b, rounded to 1 decimal.
    Supports tuples (lat, lon), dicts, and point-like objects.
    """
    def extract_lat_lon(pt: Any) -> tuple[float, float]:
        if isinstance(pt, tuple) or isinstance(pt, list):
            return float(pt[0]), float(pt[1])
        if isinstance(pt, dict):
            lat = pt.get("latitude") or pt.get("lat") or pt.get("y")
            lon = pt.get("longitude") or pt.get("lon") or pt.get("x")
            if lat is not None and lon is not None:
                return float(lat), float(lon)
        lat = getattr(pt, "latitude", getattr(pt, "lat", getattr(pt, "y", None)))
        lon = getattr(pt, "longitude", getattr(pt, "lon", getattr(pt, "x", None)))
        if lat is not None and lon is not None:
            return float(lat), float(lon)
        raise ValueError(f"Could not extract coordinates from point: {pt}")

    lat1, lon1 = extract_lat_lon(point_a)
    lat2, lon2 = extract_lat_lon(point_b)
    return round(haversine_distance(lat1, lon1, lat2, lon2), 1)


def get_nearby_markets(db: Session, farm_id: int, radius_km: float = 100.0, limit: int = 15) -> Dict[str, Any]:
    """
    Retrieve nearest markets within radius_km, ordered by distance ascending.
    If 0 markets exist within radius_km, fetches nearest market outside radius_km.
    """
    farm = db.get(Farm, farm_id)
    if not farm:
        return {"markets": [], "note": f"Farm with ID {farm_id} not found."}

    if farm.location is None:
        return {"markets": [], "note": "Farm has no location geometry coordinates."}

    try:
        point: Point = to_shape(farm.location)
        farm_lat, farm_lon = point.y, point.x
    except Exception:
        return {"markets": [], "note": "Error parsing farm location coordinates."}

    def _extract_market_dict(m: Market, dist_km: float, is_within: bool) -> Dict[str, Any]:
        market_point: Point = to_shape(m.location)
        mp = db.query(MarketPrice).filter(MarketPrice.market_id == m.id).order_by(MarketPrice.price_date.desc()).first()
        crop_name = None
        current_price = None
        price_unit = None
        trend = None
        if mp:
            current_price = mp.price
            price_unit = mp.price_unit
            trend = mp.trend
            crop_obj = db.get(Crop, mp.crop_id)
            if crop_obj:
                crop_name = crop_obj.name

        return {
            "market_id": m.id,
            "market_name": m.name,
            "district": m.district,
            "state": m.state,
            "distance_km": dist_km,
            "latitude": market_point.y,
            "longitude": market_point.x,
            "within_radius": is_within,
            "crop": crop_name,
            "current_price": current_price,
            "price_unit": price_unit,
            "trend": trend,
        }

    try:
        farm_geo = func.ST_GeographyFromText(f"SRID=4326;POINT({farm_lon} {farm_lat})")
        market_geo = cast(Market.location, Geography)
        radius_m = float(radius_km) * 1000.0

        results = (
            db.query(Market, func.ST_Distance(farm_geo, market_geo).label("dist_m"))
            .filter(func.ST_DWithin(farm_geo, market_geo, radius_m))
            .order_by("dist_m")
            .limit(limit)
            .all()
        )

        markets_list = []
        for m, dist_m in results:
            dist_km = round(float(dist_m) / 1000.0, 1)
            markets_list.append(_extract_market_dict(m, dist_km, True))

        # If 0 markets inside radius_km, query nearest market outside radius_km
        if not markets_list:
            nearest_outside = (
                db.query(Market, func.ST_Distance(farm_geo, market_geo).label("dist_m"))
                .order_by("dist_m")
                .first()
            )
            if nearest_outside:
                m_out, dist_m_out = nearest_outside
                dist_km_out = round(float(dist_m_out) / 1000.0, 1)
                markets_list.append(_extract_market_dict(m_out, dist_km_out, False))

        return {"markets": markets_list, "note": None}

    except Exception:
        # Fallback to python Haversine distance calculations
        markets = db.query(Market).all()
        candidates = []
        for m in markets:
            if m.location is not None:
                try:
                    m_point: Point = to_shape(m.location)
                    dist = haversine_distance(farm_lat, farm_lon, m_point.y, m_point.x)
                    is_within = dist <= radius_km
                    candidates.append({
                        "m": m,
                        "dist": dist,
                        "is_within": is_within
                    })
                except Exception:
                    pass

        candidates.sort(key=lambda x: x["dist"])
        within_candidates = [c for c in candidates if c["is_within"]][:limit]
        final_list = []
        if within_candidates:
            for item in within_candidates:
                final_list.append(_extract_market_dict(item["m"], round(item["dist"], 1), True))
        elif candidates:
            # Nearest fallback
            nearest_item = candidates[0]
            final_list.append(_extract_market_dict(nearest_item["m"], round(nearest_item["dist"], 1), False))

        return {"markets": final_list, "note": "PostGIS query fallback used."}


def get_geographic_context(db: Session, farm_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve geographical context: district, state, agro-climatic zone,
    and the number of nearby markets within 100 km radius.
    """
    farm = db.get(Farm, farm_id)
    if not farm:
        return None

    district = farm.district
    state = farm.state
    agro_climatic_zone = None

    market_count = 0
    if farm.location is not None:
        try:
            point: Point = to_shape(farm.location)
            farm_lat, farm_lon = point.y, point.x
            farm_geo = func.ST_GeographyFromText(f"SRID=4326;POINT({farm_lon} {farm_lat})")
            market_geo = cast(Market.location, Geography)
            market_count = (
                db.query(Market)
                .filter(func.ST_DWithin(farm_geo, market_geo, 100.0 * 1000.0))
                .count()
            )
        except Exception:
            try:
                markets = db.query(Market).all()
                for m in markets:
                    if m.location is not None:
                        m_point: Point = to_shape(m.location)
                        dist = haversine_distance(farm_lat, farm_lon, m_point.y, m_point.x)
                        if dist <= 100.0:
                            market_count += 1
            except Exception:
                pass

    return {
        "district": district,
        "state": state,
        "agro_climatic_zone": agro_climatic_zone,
        "nearby_market_count": market_count
    }
