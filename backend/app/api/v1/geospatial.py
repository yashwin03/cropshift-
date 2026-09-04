from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.geospatial.service import (
    get_farm_location,
    get_nearby_markets,
    get_geographic_context
)
from app.schemas.geospatial import GeospatialResponse, Coordinate, GeographicContext, NearbyMarket

router = APIRouter()

@router.get("/{farm_id}", response_model=GeospatialResponse)
def get_geospatial(
    farm_id: int,
    radius_km: float = Query(50.0, description="Market reach radius in kilometers (25, 50, 75, 100)"),
    db: Session = Depends(get_db)
):
    loc = get_farm_location(db, farm_id)
    farm_coord = Coordinate(**loc) if loc else None

    # Get nearby markets filtered by PostGIS radius
    markets_res = get_nearby_markets(db, farm_id, radius_km=radius_km)
    markets_list = [NearbyMarket(**m) for m in markets_res["markets"]]
    
    dist_info = markets_res["note"]
    if not dist_info and markets_list:
        nearest = markets_list[0]
        if nearest.within_radius:
            dist_info = f"Nearest market is {nearest.market_name} at {nearest.distance_km:.1f} km straight-line."
        else:
            dist_info = f"No markets within {radius_km:.0f} km. Nearest market is {nearest.market_name} at {nearest.distance_km:.1f} km straight-line."

    ctx = get_geographic_context(db, farm_id)
    if not ctx:
        raise HTTPException(status_code=404, detail="Geographic context not found for this farm.")

    geo_ctx = GeographicContext(
        district=ctx["district"],
        state=ctx["state"],
        agro_climatic_zone=ctx["agro_climatic_zone"],
        markets_count=ctx["nearby_market_count"]
    )

    return GeospatialResponse(
        farm=farm_coord,
        nearby_markets=markets_list,
        distance_information=dist_info,
        geographic_context=geo_ctx
    )
