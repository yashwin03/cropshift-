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
from .farms import resolve_farmer_farm
from ...services.market_service import validate_target_price_bounds


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
        quality_cert_filename=getattr(lot, 'quality_cert_filename', None),
        quality_cert_url=getattr(lot, 'quality_cert_url', None),
        quality_cert_uploaded_at=getattr(lot, 'quality_cert_uploaded_at', None),
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

    asking_price = payload.asking_price_per_quintal or future_lot.asking_price_per_quintal
    if asking_price is not None:
        validate_target_price_bounds(db, future_lot.crop_id, asking_price, future_lot.farm_id)

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
        asking_price_per_quintal=asking_price,
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
    # Verify farm exists and belongs to farmer via canonical ownership resolver
    farm = resolve_farmer_farm(db, current_user, payload.farm_id)

    crop = db.query(Crop).filter(Crop.id == payload.crop_id).first()
    if not crop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crop {payload.crop_id} not found",
        )

    if payload.asking_price_per_quintal is not None:
        validate_target_price_bounds(db, payload.crop_id, payload.asking_price_per_quintal, farm.id)

    # Duplicate protection check (Requirement 5)
    existing_stock = (
        db.query(StockLot)
        .filter(
            StockLot.farmer_id == current_user.id,
            StockLot.farm_id == payload.farm_id,
            StockLot.crop_id == payload.crop_id,
            StockLot.actual_quantity_quintals == payload.actual_quantity_quintals,
            StockLot.status.in_([StockLotStatus.DRAFT, StockLotStatus.AVAILABLE])
        )
        .first()
    )
    if existing_stock:
        return _build_stock_lot_response(existing_stock)

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

    if payload.asking_price_per_quintal is not None:
        validate_target_price_bounds(db, stock_lot.crop_id, payload.asking_price_per_quintal, stock_lot.farm_id)

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

    if not stock_lot.quality_cert_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quality certificate is required for already harvested crops.",
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
    Marketplace discovery endpoint for AVAILABLE harvested stock (Oilseeds only).
    Shields private farmer contact info and exact PostGIS GPS coordinates.
    """
    lots = (
        db.query(StockLot)
        .join(Crop, StockLot.crop_id == Crop.id)
        .filter(
            StockLot.status == StockLotStatus.AVAILABLE,
            StockLot.available_quantity_quintals > 0,
            Crop.is_oilseed == True,
        )
        .order_by(StockLot.actual_harvest_date.desc())
        .all()
    )

    seen_ids = set()
    result = []
    for lot in lots:
        if lot.id in seen_ids:
            continue
        seen_ids.add(lot.id)
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
                quality_cert_filename=getattr(lot, 'quality_cert_filename', None),
                quality_cert_url=getattr(lot, 'quality_cert_url', None),
                quality_cert_uploaded_at=getattr(lot, 'quality_cert_uploaded_at', None),
                district=lot.farm.district if lot.farm else None,
                state=lot.farm.state if lot.farm else None,
                status=lot.status,
            )
        )

    return result


import os
import re
from datetime import datetime
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

@router.post(
    "/farmer/stock-lots/{stock_id}/quality-certificate",
    response_model=StockLotResponse,
    summary="Upload a quality certificate document for a harvested stock lot",
)
async def upload_quality_certificate(
    stock_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER, UserRole.BUYER)),
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

    filename = file.filename or "quality_cert.pdf"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    allowed_exts = {"pdf", "jpg", "jpeg", "png"}
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF, JPG, or PNG document.",
        )

    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 10MB limit. Please upload a smaller document.",
        )

    safe_name = re.sub(r'[^a-zA-Z0-9_\.-]', '_', filename)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    stored_filename = f"lot_{stock_id}_{timestamp_str}_{safe_name}"

    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads/quality_certs"))
    os.makedirs(uploads_dir, exist_ok=True)
    file_path = os.path.join(uploads_dir, stored_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    stock_lot.quality_cert_filename = filename
    stock_lot.quality_cert_url = f"/uploads/quality_certs/{stored_filename}"
    stock_lot.quality_cert_uploaded_at = datetime.utcnow()

    db.commit()
    db.refresh(stock_lot)

    return _build_stock_lot_response(stock_lot)


@router.get(
    "/stock-lots/{stock_id}/certificate",
    summary="Download or view quality certificate for a harvested stock lot",
)
def get_stock_lot_certificate(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stock_lot = db.query(StockLot).filter(StockLot.id == stock_id).first()
    if not stock_lot or not stock_lot.quality_cert_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quality certificate not found for this stock lot",
        )

    # Access control check: Draft certificates are only accessible to the owning farmer
    if stock_lot.status == StockLotStatus.DRAFT and stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view the quality certificate for this draft stock lot",
        )

    rel_path = stock_lot.quality_cert_url.lstrip("/")
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../", rel_path))
    if not os.path.exists(abs_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Certificate file does not exist on server",
        )

    filename = stock_lot.quality_cert_filename or f"quality_cert_{stock_id}.pdf"
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    media_type = "application/pdf"
    if ext in ["jpg", "jpeg"]:
        media_type = "image/jpeg"
    elif ext == "png":
        media_type = "image/png"

    return FileResponse(
        abs_path,
        media_type=media_type,
        filename=filename,
        headers={
            "Content-Disposition": f"inline; filename=\"{filename}\"",
            "Access-Control-Expose-Headers": "Content-Disposition",
        }
    )

