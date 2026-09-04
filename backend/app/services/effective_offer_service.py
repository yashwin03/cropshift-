"""Effective Offer calculation service."""
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.models.bid import Bid
from app.models.market import Market
from app.geospatial.service import get_farm_location, distance_km


# Demo/MVP freight rate per kilometer (INR / km)
MVP_FREIGHT_RATE_PER_KM = 50.0


def compute_effective_offer(db: Session, bid: Bid) -> Tuple[Optional[float], Optional[str]]:
    """
    Calculate Effective Offer Price (₹/Quintal) dynamically:
    Effective Price = Offered Price - ( (Distance_km * Rate_per_km) / Quantity_quintals )

    If farm location or delivery destination coordinates are unavailable,
    returns (None, "Destination location unavailable") without fabricating fake distances.
    """
    if not bid.lot or not bid.lot.farm:
        return None, "Destination location unavailable"

    farm_coords = get_farm_location(db, bid.lot.farm_id)
    if not farm_coords:
        return None, "Destination location unavailable"

    # Check destination market via linked demand or delivery market
    dest_market = None
    if bid.lot.demand and bid.lot.demand.delivery_market_id:
        dest_market = db.get(Market, bid.lot.demand.delivery_market_id)
    elif bid.lot.farm.district:
        # Search for mandi market in the same district
        dest_market = db.query(Market).filter(Market.district.ilike(f"%{bid.lot.farm.district}%")).first()

    if not dest_market or dest_market.location is None:
        return None, "Destination location unavailable"

    try:
        from geoalchemy2.shape import to_shape
        m_point = to_shape(dest_market.location)
        dest_coords = {"latitude": float(m_point.y), "longitude": float(m_point.x)}
        dist_km = distance_km(farm_coords, dest_coords)

        if bid.quantity_quintals <= 0:
            return None, "Invalid quantity for transport calculation"

        total_freight_cost = dist_km * MVP_FREIGHT_RATE_PER_KM
        freight_per_quintal = total_freight_cost / bid.quantity_quintals
        effective_price = round(bid.offered_price_per_quintal - freight_per_quintal, 2)
        return effective_price, None
    except Exception:
        return None, "Destination location unavailable"


def compute_effective_stock_offer(db: Session, stock_bid) -> Tuple[Optional[float], Optional[str]]:
    """Calculate Effective Offer Price (₹/Quintal) for a post-harvest StockBid."""
    stock_lot = stock_bid.stock_lot
    if not stock_lot or not stock_lot.farm:
        return None, "Destination location unavailable"

    farm_coords = get_farm_location(db, stock_lot.farm_id)
    if not farm_coords:
        return None, "Destination location unavailable"

    dest_market = None
    if stock_lot.farm.district:
        dest_market = db.query(Market).filter(Market.district.ilike(f"%{stock_lot.farm.district}%")).first()

    if not dest_market or dest_market.location is None:
        return None, "Destination location unavailable"

    try:
        from geoalchemy2.shape import to_shape
        m_point = to_shape(dest_market.location)
        dest_coords = {"latitude": float(m_point.y), "longitude": float(m_point.x)}
        dist_km = distance_km(farm_coords, dest_coords)

        qty = stock_bid.requested_quantity_quintals
        if qty <= 0:
            return None, "Invalid quantity for transport calculation"

        total_freight_cost = dist_km * MVP_FREIGHT_RATE_PER_KM
        freight_per_quintal = total_freight_cost / qty
        effective_price = round(stock_bid.offered_price_per_quintal - freight_per_quintal, 2)
        return effective_price, None
    except Exception:
        return None, "Destination location unavailable"
