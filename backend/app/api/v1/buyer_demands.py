"""Buyer Demands API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User, UserRole
from ...models.crop import Crop
from ...models.market import Market
from ...models.buyer_demand import BuyerDemand, BuyerDemandStatus
from ...schemas.buyer_demand import (
    BuyerDemandCreate,
    BuyerDemandUpdate,
    BuyerDemandResponse,
    BuyerDemandFarmerView,
)
from .auth import get_current_user, require_role

router = APIRouter()


def _enrich_demand_response(demand: BuyerDemand) -> BuyerDemandResponse:
    res = BuyerDemandResponse.model_validate(demand)
    if demand.crop:
        res.crop_name = demand.crop.name
    if demand.delivery_market:
        res.delivery_market_name = demand.delivery_market.name
    if demand.buyer:
        res.buyer_company_name = f"{demand.buyer.username}'s Procurement"
    return res


def _enrich_farmer_view(demand: BuyerDemand) -> BuyerDemandFarmerView:
    res = BuyerDemandFarmerView.model_validate(demand)
    if demand.crop:
        res.crop_name = demand.crop.name
    if demand.delivery_market:
        res.delivery_market_name = demand.delivery_market.name
    if demand.buyer:
        res.company_name = f"{demand.buyer.username} Wholesale"
    if demand.created_at:
        res.posted_date = demand.created_at.strftime("%Y-%m-%d")
    return res


# --- BUYER ENDPOINTS ---

@router.post("/buyer/demands", response_model=BuyerDemandResponse, status_code=status.HTTP_201_CREATED)
def create_buyer_demand(
    payload: BuyerDemandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Create a new Buyer Procurement Demand (BUYER role required)."""
    # Verify crop_id exists
    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with id {payload.crop_id} not found."
        )

    # Verify optional delivery_market_id if provided
    if payload.delivery_market_id:
        mkt = db.query(Market).filter(Market.id == payload.delivery_market_id).first()
        if not mkt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Market with id {payload.delivery_market_id} not found."
            )

    demand = BuyerDemand(
        buyer_id=current_user.id,
        crop_id=payload.crop_id,
        variety=payload.variety,
        quantity_quintals=payload.quantity_quintals,
        target_price_per_quintal=payload.target_price_per_quintal,
        delivery_district=payload.delivery_district,
        delivery_state=payload.delivery_state,
        delivery_market_id=payload.delivery_market_id,
        expected_harvest_start=payload.expected_harvest_start,
        expected_harvest_end=payload.expected_harvest_end,
        quality_grade=payload.quality_grade,
        status=BuyerDemandStatus.ACTIVE,
    )
    db.add(demand)
    db.commit()
    db.refresh(demand)
    return _enrich_demand_response(demand)


@router.get("/buyer/demands/me", response_model=List[BuyerDemandResponse])
def get_my_buyer_demands(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Retrieve all demands created by the authenticated Buyer."""
    demands = (
        db.query(BuyerDemand)
        .filter(BuyerDemand.buyer_id == current_user.id)
        .order_by(BuyerDemand.created_at.desc())
        .all()
    )
    return [_enrich_demand_response(d) for d in demands]


@router.get("/buyer/demands/{demand_id}", response_model=BuyerDemandResponse)
def get_buyer_demand_by_id(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Retrieve a specific demand by ID (Owner Buyer only)."""
    demand = db.query(BuyerDemand).filter(BuyerDemand.id == demand_id).first()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Buyer demand {demand_id} not found."
        )
    if demand.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access permission for this demand."
        )
    return _enrich_demand_response(demand)


@router.put("/buyer/demands/{demand_id}", response_model=BuyerDemandResponse)
def update_buyer_demand(
    demand_id: int,
    payload: BuyerDemandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Update an ACTIVE Buyer Demand (Owner Buyer only)."""
    demand = db.query(BuyerDemand).filter(BuyerDemand.id == demand_id).first()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Buyer demand {demand_id} not found."
        )
    if demand.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this demand."
        )
    if demand.status != BuyerDemandStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit demand in {demand.status.value} status."
        )

    # Validate crop if changing
    if payload.crop_id and payload.crop_id != demand.crop_id:
        crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
        if not crop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop with id {payload.crop_id} not found."
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(demand, field, value)

    db.commit()
    db.refresh(demand)
    return _enrich_demand_response(demand)


@router.delete("/buyer/demands/{demand_id}", response_model=BuyerDemandResponse)
def cancel_buyer_demand(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Cancel an active Buyer Demand (Soft state transition to CANCELLED)."""
    demand = db.query(BuyerDemand).filter(BuyerDemand.id == demand_id).first()
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Buyer demand {demand_id} not found."
        )
    if demand.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this demand."
        )

    demand.status = BuyerDemandStatus.CANCELLED
    db.commit()
    db.refresh(demand)
    return _enrich_demand_response(demand)


# --- FARMER DISCOVERY ENDPOINT ---

@router.get("/demands/active", response_model=List[BuyerDemandFarmerView])
def get_active_demands_for_discovery(
    crop_id: Optional[int] = Query(None, description="Filter by crop ID"),
    district: Optional[str] = Query(None, description="Filter by delivery district"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Farmer discovery listing of ACTIVE buyer demands."""
    query = db.query(BuyerDemand).filter(BuyerDemand.status == BuyerDemandStatus.ACTIVE)

    if crop_id:
        query = query.filter(BuyerDemand.crop_id == crop_id)
    if district:
        query = query.filter(BuyerDemand.delivery_district.ilike(f"%{district}%"))

    demands = query.order_by(BuyerDemand.created_at.desc()).all()
    return [_enrich_farmer_view(d) for d in demands]
