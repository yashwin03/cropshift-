from fastapi import APIRouter
from app.api.v1 import (
    health,
    recommendations,
    profitability,
    markets,
    subsidies,
    geospatial,
    risk,
    ivr,
    auth,
    farms,
    buyer_demands,
    future_crop_lots,
    bids,
    contact_sharing,
    stock_lots,
    stock_bids,
    trade_orders,
    peer_proof,
    crop_cultivation,
    ratings,
    reports,
)

api_router = APIRouter()

# Include v1 routers
api_router.include_router(health.router)
api_router.include_router(farms.router, prefix="/farms", tags=["Farms"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(peer_proof.router, prefix="/peer-proof", tags=["Peer Proof"])
api_router.include_router(crop_cultivation.router, prefix="/cultivation-records", tags=["Cultivation Records"])
api_router.include_router(profitability.router, prefix="/profitability", tags=["Profitability"])
api_router.include_router(markets.router, prefix="/markets", tags=["Markets"])
api_router.include_router(subsidies.router, prefix="/subsidies", tags=["Subsidies"])
api_router.include_router(geospatial.router, prefix="/geospatial", tags=["Geospatial"])
api_router.include_router(risk.router, prefix="/risk-simulation", tags=["Risk Simulation"])
api_router.include_router(ivr.router, prefix="/ivr", tags=["IVR"])
api_router.include_router(auth.router)
api_router.include_router(buyer_demands.router, tags=["Buyer Demands"])
api_router.include_router(future_crop_lots.router, tags=["Future Crop Lots"])
api_router.include_router(bids.router, tags=["Bids"])
api_router.include_router(contact_sharing.router, tags=["Contact Sharing"])
api_router.include_router(stock_lots.router, tags=["Stock Lots"])
api_router.include_router(stock_bids.router, tags=["Stock Bids"])
api_router.include_router(trade_orders.router, tags=["Trade Orders"])
api_router.include_router(ratings.router)
api_router.include_router(reports.router)

