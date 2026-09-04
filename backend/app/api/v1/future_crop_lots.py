"""Future Crop Lots API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User, UserRole
from ...models.farm import Farm
from ...models.crop import Crop
from ...models.buyer_demand import BuyerDemand, BuyerDemandStatus
from ...models.recommendation import Recommendation
from ...models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from ...schemas.future_crop_lot import (
    FutureCropLotCreate,
    FutureCropLotUpdate,
    FutureCropLotResponse,
    FutureCropLotMarketplaceView,
)
from .auth import get_current_user, require_role

router = APIRouter()


def _verify_farm_ownership(farm: Farm, current_user: User):
    """Verify farm exists and is owned by the current authenticated user."""
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found."
        )
    # Check owner_id or farmer relationship
    if farm.owner_id and farm.owner_id == current_user.id:
        return True
    if farm.farmer and getattr(farm.farmer, "user_id", None) == current_user.id:
        return True
    if farm.farmer_id == current_user.id:
        return True
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not own this farm."
    )


def _enrich_lot_response(lot: FutureCropLot) -> FutureCropLotResponse:
    res = FutureCropLotResponse.model_validate(lot)
    if lot.farm:
        res.farm_name = f"Farm #{lot.farm.id} ({lot.farm.district or 'Local'})"
        res.district = lot.farm.district
        res.state = lot.farm.state
    if lot.crop:
        res.crop_name = lot.crop.name
    if lot.demand:
        res.demand_title = f"Buyer Demand #{lot.demand.id} ({lot.demand.delivery_district})"
    return res



def _enrich_marketplace_view(lot: FutureCropLot) -> FutureCropLotMarketplaceView:
    res = FutureCropLotMarketplaceView.model_validate(lot)
    if lot.farm:
        res.district = lot.farm.district
        res.state = lot.farm.state
    if lot.crop:
        res.crop_name = lot.crop.name
    if lot.demand:
        res.demand_title = f"Buyer Demand #{lot.demand.id}"
    res.farmer_display_id = f"Farmer #{lot.farmer_id}"
    return res


# --- FARMER ENDPOINTS ---

@router.post("/farmer/future-crop-lots", response_model=FutureCropLotResponse, status_code=status.HTTP_201_CREATED)
def create_future_crop_lot(
    payload: FutureCropLotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Create a new Future Crop Lot (FARMER role required)."""
    # 1. Verify Farm & Ownership
    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
    _verify_farm_ownership(farm, current_user)

    # 2. Verify Crop
    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop with id {payload.crop_id} not found."
        )

    # 3. Verify optional demand_id linkage
    if payload.demand_id:
        demand = db.query(BuyerDemand).filter(BuyerDemand.id == payload.demand_id).first()
        if not demand:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Buyer demand {payload.demand_id} not found."
            )
        if demand.status != BuyerDemandStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot link to buyer demand with status '{demand.status.value}'."
            )
        if demand.crop_id != payload.crop_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Future crop lot crop ({crop.name}) does not match buyer demand crop (id {demand.crop_id})."
            )

    # 4. Verify optional recommendation_id linkage
    if payload.recommendation_id:
        rec = db.query(Recommendation).filter(Recommendation.id == payload.recommendation_id).first()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recommendation with id {payload.recommendation_id} not found."
            )
        if rec.farm_id != payload.farm_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recommendation does not belong to the selected farm."
            )

    initial_status = payload.status or FutureCropLotStatus.DRAFT

    lot = FutureCropLot(
        farm_id=payload.farm_id,
        farmer_id=current_user.id,
        crop_id=payload.crop_id,
        demand_id=payload.demand_id,
        recommendation_id=payload.recommendation_id,
        variety=payload.variety,
        planned_acres=payload.planned_acres,
        expected_quantity_quintals=payload.expected_quantity_quintals,
        asking_price_per_quintal=payload.asking_price_per_quintal,
        planned_sowing_date=payload.planned_sowing_date,
        expected_harvest_start=payload.expected_harvest_start,
        expected_harvest_end=payload.expected_harvest_end,
        quality_grade=payload.quality_grade,
        status=initial_status,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return _enrich_lot_response(lot)


@router.get("/farmer/future-crop-lots/me", response_model=List[FutureCropLotResponse])
def get_my_future_crop_lots(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Retrieve all Future Crop Lots created by current Farmer."""
    lots = (
        db.query(FutureCropLot)
        .filter(FutureCropLot.farmer_id == current_user.id)
        .order_by(FutureCropLot.created_at.desc())
        .all()
    )
    return [_enrich_lot_response(l) for l in lots]


@router.get("/farmer/future-crop-lots/{lot_id}", response_model=FutureCropLotResponse)
def get_future_crop_lot_by_id(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Retrieve a specific Future Crop Lot by ID (Owner Farmer only)."""
    lot = db.query(FutureCropLot).filter(FutureCropLot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {lot_id} not found."
        )
    if lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access permission for this lot."
        )
    return _enrich_lot_response(lot)


@router.put("/farmer/future-crop-lots/{lot_id}", response_model=FutureCropLotResponse)
def update_future_crop_lot(
    lot_id: int,
    payload: FutureCropLotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Update an active Future Crop Lot (Owner Farmer only, status DRAFT/OPEN)."""
    lot = db.query(FutureCropLot).filter(FutureCropLot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {lot_id} not found."
        )
    if lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this lot."
        )
    if lot.status not in (FutureCropLotStatus.DRAFT, FutureCropLotStatus.OPEN):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit future crop lot in '{lot.status.value}' status."
        )

    # If updating farm_id, verify ownership
    if payload.farm_id and payload.farm_id != lot.farm_id:
        farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
        _verify_farm_ownership(farm, current_user)

    # If updating demand_id, verify active status and crop match
    target_crop_id = payload.crop_id or lot.crop_id
    if payload.demand_id and payload.demand_id != lot.demand_id:
        demand = db.query(BuyerDemand).filter(BuyerDemand.id == payload.demand_id).first()
        if not demand or demand.status != BuyerDemandStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Linked buyer demand is not active."
            )
        if demand.crop_id != target_crop_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Future crop lot crop does not match buyer demand crop."
            )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lot, field, value)

    db.commit()
    db.refresh(lot)
    return _enrich_lot_response(lot)


@router.post("/farmer/future-crop-lots/{lot_id}/publish", response_model=FutureCropLotResponse)
def publish_future_crop_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Publish a DRAFT lot to OPEN status (Owner Farmer only)."""
    lot = db.query(FutureCropLot).filter(FutureCropLot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {lot_id} not found."
        )
    if lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to publish this lot."
        )

    lot.status = FutureCropLotStatus.OPEN
    db.commit()
    db.refresh(lot)
    return _enrich_lot_response(lot)


@router.delete("/farmer/future-crop-lots/{lot_id}", response_model=FutureCropLotResponse)
def cancel_future_crop_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Cancel a Future Crop Lot (Soft state transition to CANCELLED)."""
    lot = db.query(FutureCropLot).filter(FutureCropLot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {lot_id} not found."
        )
    if lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to cancel this lot."
        )

    lot.status = FutureCropLotStatus.CANCELLED
    db.commit()
    db.refresh(lot)
    return _enrich_lot_response(lot)


# --- MARKETPLACE DISCOVERY ENDPOINT ---

@router.get("/future-crop-lots/open", response_model=List[FutureCropLotMarketplaceView])
def get_open_future_crop_lots_for_discovery(
    crop_id: Optional[int] = Query(None, description="Filter by crop ID"),
    district: Optional[str] = Query(None, description="Filter by district"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Marketplace discovery of OPEN Future Crop Lots."""
    query = (
        db.query(FutureCropLot)
        .join(Farm, FutureCropLot.farm_id == Farm.id)
        .filter(FutureCropLot.status == FutureCropLotStatus.OPEN)
    )

    if crop_id:
        query = query.filter(FutureCropLot.crop_id == crop_id)
    if district:
        query = query.filter(Farm.district.ilike(f"%{district}%"))

    lots = query.order_by(FutureCropLot.created_at.desc()).all()
    return [_enrich_marketplace_view(l) for l in lots]
