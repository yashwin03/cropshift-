"""StockLot API endpoints for farmer harvest management and buyer stock discovery."""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User, UserRole
from ...models.farm import Farm
from ...models.crop import Crop
from ...models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from ...models.stock_lot import StockLot, StockLotStatus
from ...schemas.stock_lot import (
    HarvestRequest,
    StockLotCreate,
    StockLotUpdate,
    StockLotResponse,
    StockLotMarketplaceView,
)
from .auth import get_current_user, require_role

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_stock_lot_response(lot: StockLot) -> StockLotResponse:
    crop_name = lot.crop.name if lot.crop else None
    farm_name = f"{lot.farm.district} Farm" if (lot.farm and lot.farm.district) else f"Farm #{lot.farm_id}"
    district = lot.farm.district if lot.farm else None
    state = lot.farm.state if lot.farm else None

    return StockLotResponse(
        id=lot.id,
        farmer_id=lot.farmer_id,
        farm_id=lot.farm_id,
        future_crop_lot_id=lot.future_crop_lot_id,
        crop_id=lot.crop_id,
        variety=lot.variety,
        actual_quantity_quintals=lot.actual_quantity_quintals,
        available_quantity_quintals=lot.available_quantity_quintals,
        actual_harvest_date=lot.actual_harvest_date,
        quality_grade=lot.quality_grade,
        asking_price_per_quintal=lot.asking_price_per_quintal,
        status=lot.status,
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        crop_name=crop_name,
        farm_name=farm_name,
        district=district,
        state=state,
    )


# ==========================================
# FARMER HARVEST & STOCK MANAGEMENT ENDPOINTS
# ==========================================

@router.post(
    "/farmer/future-crop-lots/{lot_id}/harvest",
    response_model=StockLotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record actual harvest from a FutureCropLot",
)
def harvest_future_crop_lot(
    lot_id: int,
    payload: HarvestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    future_lot = db.query(FutureCropLot).filter(FutureCropLot.id == lot_id).first()
    if not future_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {lot_id} not found",
        )

    if future_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this future crop lot",
        )

    if future_lot.status == FutureCropLotStatus.HARVESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Future crop lot has already been harvested",
        )

    if future_lot.status not in (FutureCropLotStatus.OPEN, FutureCropLotStatus.INDICATIVE_ACCEPTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Future crop lot in status {future_lot.status.value} is not eligible for harvest",
        )

    # Transition FutureCropLot status to HARVESTED
    future_lot.status = FutureCropLotStatus.HARVESTED

    # Create StockLot in DRAFT status
    stock_lot = StockLot(
        farmer_id=current_user.id,
        farm_id=future_lot.farm_id,
        future_crop_lot_id=future_lot.id,
        crop_id=future_lot.crop_id,
        variety=future_lot.variety,
        actual_quantity_quintals=payload.actual_quantity_quintals,
        available_quantity_quintals=payload.actual_quantity_quintals,
        actual_harvest_date=payload.actual_harvest_date,
        quality_grade=payload.quality_grade or future_lot.quality_grade,
        asking_price_per_quintal=payload.asking_price_per_quintal or future_lot.asking_price_per_quintal,
        status=StockLotStatus.DRAFT,
    )

    db.add(stock_lot)
    db.commit()
    db.refresh(stock_lot)

    logger.info(
        f"Farmer {current_user.id} recorded harvest for FutureCropLot {lot_id} -> StockLot {stock_lot.id} ({stock_lot.actual_quantity_quintals} Q)"
    )

    return _build_stock_lot_response(stock_lot)


@router.post(
    "/farmer/stock-lots",
    response_model=StockLotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create direct harvested stock lot without a FutureCropLot",
)
def create_direct_stock_lot(
    payload: StockLotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    # Verify farm exists and belongs to farmer
    farm = db.query(Farm).filter(Farm.id == payload.farm_id).first()
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm {payload.farm_id} not found",
        )

    # Ownership check via farmer_id or farm.owner_id
    if farm.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this farm",
        )

    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop {payload.crop_id} not found",
        )

    stock_lot = StockLot(
        farmer_id=current_user.id,
        farm_id=payload.farm_id,
        future_crop_lot_id=None,
        crop_id=payload.crop_id,
        variety=payload.variety,
        actual_quantity_quintals=payload.actual_quantity_quintals,
        available_quantity_quintals=payload.actual_quantity_quintals,
        actual_harvest_date=payload.actual_harvest_date,
        quality_grade=payload.quality_grade,
        asking_price_per_quintal=payload.asking_price_per_quintal,
        status=StockLotStatus.DRAFT,
    )

    db.add(stock_lot)
    db.commit()
    db.refresh(stock_lot)

    return _build_stock_lot_response(stock_lot)


@router.get(
    "/farmer/stock-lots/me",
    response_model=List[StockLotResponse],
    summary="Get authenticated farmer's stock lots",
)
def get_my_stock_lots(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    lots = (
        db.query(StockLot)
        .filter(StockLot.farmer_id == current_user.id)
        .order_by(StockLot.created_at.desc())
        .all()
    )
    return [_build_stock_lot_response(lot) for lot in lots]


@router.get(
    "/farmer/stock-lots/{stock_id}",
    response_model=StockLotResponse,
    summary="Get details of a specific farmer stock lot",
)
def get_stock_lot(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    stock_lot = db.query(StockLot).filter(StockLot.id == stock_id).first()
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock lot {stock_id} not found",
        )

    if stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock lot",
        )

    return _build_stock_lot_response(stock_lot)


@router.put(
    "/farmer/stock-lots/{stock_id}",
    response_model=StockLotResponse,
    summary="Update a DRAFT stock lot",
)
def update_stock_lot(
    stock_id: int,
    payload: StockLotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    stock_lot = db.query(StockLot).filter(StockLot.id == stock_id).first()
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock lot {stock_id} not found",
        )

    if stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock lot",
        )

    if stock_lot.status != StockLotStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DRAFT stock lots can be modified",
        )

    if payload.actual_quantity_quintals is not None:
        stock_lot.actual_quantity_quintals = payload.actual_quantity_quintals
        stock_lot.available_quantity_quintals = payload.actual_quantity_quintals

    if payload.actual_harvest_date is not None:
        stock_lot.actual_harvest_date = payload.actual_harvest_date

    if payload.variety is not None:
        stock_lot.variety = payload.variety

    if payload.quality_grade is not None:
        stock_lot.quality_grade = payload.quality_grade

    if payload.asking_price_per_quintal is not None:
        stock_lot.asking_price_per_quintal = payload.asking_price_per_quintal

    db.commit()
    db.refresh(stock_lot)

    return _build_stock_lot_response(stock_lot)


@router.post(
    "/farmer/stock-lots/{stock_id}/publish",
    response_model=StockLotResponse,
    summary="Publish a DRAFT stock lot to AVAILABLE",
)
def publish_stock_lot(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    stock_lot = db.query(StockLot).filter(StockLot.id == stock_id).first()
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock lot {stock_id} not found",
        )

    if stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock lot",
        )

    if stock_lot.available_quantity_quintals <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish stock lot with zero available quantity",
        )

    stock_lot.status = StockLotStatus.AVAILABLE
    db.commit()
    db.refresh(stock_lot)

    return _build_stock_lot_response(stock_lot)


@router.delete(
    "/farmer/stock-lots/{stock_id}",
    response_model=StockLotResponse,
    summary="Cancel a stock lot",
)
def cancel_stock_lot(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    stock_lot = db.query(StockLot).filter(StockLot.id == stock_id).first()
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock lot {stock_id} not found",
        )

    if stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock lot",
        )

    stock_lot.status = StockLotStatus.CANCELLED

    # Transition outstanding SUBMITTED bids to EXPIRED
    from ...models.stock_bid import StockBid, StockBidStatus
    submitted_bids = (
        db.query(StockBid)
        .filter(
            StockBid.stock_lot_id == stock_id,
            StockBid.status == StockBidStatus.SUBMITTED,
        )
        .all()
    )
    for b in submitted_bids:
        b.status = StockBidStatus.EXPIRED

    db.commit()
    db.refresh(stock_lot)

    return _build_stock_lot_response(stock_lot)


# ==========================================
# BUYER / PUBLIC STOCK DISCOVERY ENDPOINTS
# ==========================================

@router.get(
    "/stock-lots/open",
    response_model=List[StockLotMarketplaceView],
    summary="Discover available harvested stock lots on the marketplace",
)
def get_open_stock_lots(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Marketplace discovery endpoint for AVAILABLE harvested stock.
    Shields private farmer contact info and exact PostGIS GPS coordinates.
    """
    lots = (
        db.query(StockLot)
        .filter(
            StockLot.status == StockLotStatus.AVAILABLE,
            StockLot.available_quantity_quintals > 0,
        )
        .order_by(StockLot.actual_harvest_date.desc())
        .all()
    )

    result = []
    for lot in lots:
        result.append(
            StockLotMarketplaceView(
                id=lot.id,
                crop_id=lot.crop_id,
                crop_name=lot.crop.name if lot.crop else None,
                variety=lot.variety,
                available_quantity_quintals=lot.available_quantity_quintals,
                actual_harvest_date=lot.actual_harvest_date,
                quality_grade=lot.quality_grade,
                asking_price_per_quintal=lot.asking_price_per_quintal,
                district=lot.farm.district if lot.farm else None,
                state=lot.farm.state if lot.farm else None,
                status=lot.status,
            )
        )

    return result
