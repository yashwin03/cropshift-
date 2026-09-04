"""StockBid API endpoints for post-harvest physical stock bidding and mutual contact sharing."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User, UserRole
from ...models.stock_lot import StockLot, StockLotStatus
from ...models.stock_bid import StockBid, StockBidStatus
from ...models.contact_sharing import ContactSharing, ContactSharingStatus
from ...models.trade_order import TradeOrder, TradeOrderStatus
from ...schemas.stock_bid import (
    StockBidCreate,
    StockBidAcceptRequest,
    StockBidResponse,
    StockBidFarmerView,
)
from ...schemas.contact_sharing import (
    ContactSharingResponse,
    ContactDetails,
)
from ...services.effective_offer_service import compute_effective_stock_offer
from .auth import get_current_user, require_role

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_stock_bid_response(bid: StockBid, db: Session) -> StockBidResponse:
    stock_lot = bid.stock_lot
    crop_name = stock_lot.crop.name if (stock_lot and stock_lot.crop) else None
    district = stock_lot.farm.district if (stock_lot and stock_lot.farm) else None
    buyer_display_id = f"Buyer #{bid.buyer_id}"
    if bid.buyer and bid.buyer.full_name:
        buyer_display_id = bid.buyer.full_name

    effective_price, note = compute_effective_stock_offer(db, bid)

    return StockBidResponse(
        id=bid.id,
        stock_lot_id=bid.stock_lot_id,
        buyer_id=bid.buyer_id,
        offered_price_per_quintal=bid.offered_price_per_quintal,
        requested_quantity_quintals=bid.requested_quantity_quintals,
        allocated_quantity_quintals=bid.allocated_quantity_quintals,
        conditions=bid.conditions,
        status=bid.status,
        created_at=bid.created_at,
        updated_at=bid.updated_at,
        crop_name=crop_name,
        district=district,
        buyer_display_id=buyer_display_id,
        effective_offer_per_quintal=effective_price,
        effective_offer_note=note,
    )


# ==========================================
# BUYER POST-HARVEST STOCK BID ENDPOINTS
# ==========================================

@router.post(
    "/stock-lots/{stock_id}/bids",
    response_model=StockBidResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a post-harvest StockBid on physical inventory",
)
def create_stock_bid(
    stock_id: int,
    payload: StockBidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    stock_lot = db.query(StockLot).filter(StockLot.id == stock_id).first()
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock lot {stock_id} not found",
        )

    if stock_lot.status not in (StockLotStatus.AVAILABLE, StockLotStatus.PARTIALLY_SOLD):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock lot in status {stock_lot.status.value} is not open for bidding",
        )

    if stock_lot.available_quantity_quintals <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock lot has no available quantity remaining",
        )

    if payload.offered_price_per_quintal <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offered price per quintal must be greater than 0",
        )

    if payload.requested_quantity_quintals <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity in quintals must be greater than 0",
        )

    if payload.requested_quantity_quintals > stock_lot.available_quantity_quintals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity ({payload.requested_quantity_quintals} Q) exceeds available stock quantity ({stock_lot.available_quantity_quintals} Q)",
        )

    stock_bid = StockBid(
        stock_lot_id=stock_lot.id,
        buyer_id=current_user.id,
        offered_price_per_quintal=payload.offered_price_per_quintal,
        requested_quantity_quintals=payload.requested_quantity_quintals,
        allocated_quantity_quintals=0.0,
        conditions=payload.conditions,
        status=StockBidStatus.SUBMITTED,
    )

    db.add(stock_bid)
    db.commit()
    db.refresh(stock_bid)

    logger.info(
        f"Buyer {current_user.id} submitted StockBid {stock_bid.id} for StockLot {stock_lot.id} ({payload.requested_quantity_quintals} Q @ ₹{payload.offered_price_per_quintal}/Q)"
    )

    return _build_stock_bid_response(stock_bid, db)


@router.get(
    "/stock-bids/me",
    response_model=List[StockBidResponse],
    summary="Get authenticated buyer's submitted stock bids",
)
def get_my_stock_bids(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    bids = (
        db.query(StockBid)
        .filter(StockBid.buyer_id == current_user.id)
        .order_by(StockBid.created_at.desc())
        .all()
    )
    return [_build_stock_bid_response(b, db) for b in bids]


@router.post(
    "/stock-bids/{bid_id}/withdraw",
    response_model=StockBidResponse,
    summary="Withdraw a SUBMITTED post-harvest stock bid",
)
def withdraw_stock_bid(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock bid {bid_id} not found",
        )

    if bid.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock bid",
        )

    if bid.status != StockBidStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw bid in status {bid.status.value}",
        )

    bid.status = StockBidStatus.WITHDRAWN
    db.commit()
    db.refresh(bid)

    return _build_stock_bid_response(bid, db)


# ==========================================
# FARMER INCOMING STOCK BIDS & ACCEPTANCE
# ==========================================

@router.get(
    "/farmer/stock-lots/{stock_id}/bids",
    response_model=List[StockBidFarmerView],
    summary="Get incoming stock bids for a farmer-owned StockLot",
)
def get_farmer_stock_lot_bids(
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

    bids = (
        db.query(StockBid)
        .filter(StockBid.stock_lot_id == stock_id)
        .order_by(StockBid.created_at.desc())
        .all()
    )

    result = []
    for bid in bids:
        buyer_display_id = f"Buyer #{bid.buyer_id}"
        if bid.buyer and bid.buyer.full_name:
            buyer_display_id = bid.buyer.full_name

        effective_price, note = compute_effective_stock_offer(db, bid)

        result.append(
            StockBidFarmerView(
                id=bid.id,
                stock_lot_id=bid.stock_lot_id,
                buyer_display_id=buyer_display_id,
                offered_price_per_quintal=bid.offered_price_per_quintal,
                requested_quantity_quintals=bid.requested_quantity_quintals,
                allocated_quantity_quintals=bid.allocated_quantity_quintals,
                conditions=bid.conditions,
                status=bid.status,
                effective_offer_per_quintal=effective_price,
                effective_offer_note=note,
                created_at=bid.created_at,
            )
        )

    # Sort bids by effective offer descending if present
    result.sort(
        key=lambda b: b.effective_offer_per_quintal if b.effective_offer_per_quintal is not None else b.offered_price_per_quintal,
        reverse=True,
    )

    return result


@router.post(
    "/stock-bids/{bid_id}/accept",
    response_model=StockBidResponse,
    summary="Accept a post-harvest StockBid with quantity allocation (Concurrency Safe)",
)
def accept_stock_bid(
    bid_id: int,
    payload: StockBidAcceptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock bid {bid_id} not found",
        )

    # Atomic transaction with row-level lock on StockLot
    stock_lot = (
        db.query(StockLot)
        .filter(StockLot.id == bid.stock_lot_id)
        .with_for_update()
        .first()
    )
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock lot {bid.stock_lot_id} not found",
        )

    if stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock lot",
        )

    if bid.status != StockBidStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stock bid is in status {bid.status.value} and cannot be accepted",
        )

    allocated_qty = payload.allocated_quantity_quintals
    if allocated_qty <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Allocated quantity must be greater than 0",
        )

    if allocated_qty > bid.requested_quantity_quintals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allocated quantity ({allocated_qty} Q) cannot exceed requested quantity ({bid.requested_quantity_quintals} Q)",
        )

    if allocated_qty > stock_lot.available_quantity_quintals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Allocated quantity ({allocated_qty} Q) exceeds current available stock ({stock_lot.available_quantity_quintals} Q)",
        )

    # Update StockBid status and allocated quantity
    bid.status = StockBidStatus.ACCEPTED
    bid.allocated_quantity_quintals = allocated_qty

    # Decrement available quantity on StockLot
    stock_lot.available_quantity_quintals -= allocated_qty

    # Update StockLot status based on remaining quantity
    if stock_lot.available_quantity_quintals == 0:
        stock_lot.status = StockLotStatus.SOLD
    elif allocated_qty > 0:
        stock_lot.status = StockLotStatus.PARTIALLY_SOLD

    # Create or update ContactSharing record for this StockBid
    sharing = db.query(ContactSharing).filter(ContactSharing.stock_bid_id == bid.id).first()
    if not sharing:
        sharing = ContactSharing(
            stock_bid_id=bid.id,
            farmer_id=stock_lot.farmer_id,
            buyer_id=bid.buyer_id,
            farmer_consented=False,
            buyer_consented=False,
            status=ContactSharingStatus.PENDING,
        )
        db.add(sharing)

    # Create TradeOrder for this accepted StockBid allocation (if not already created)
    trade_order = db.query(TradeOrder).filter(TradeOrder.stock_bid_id == bid.id).first()
    if not trade_order:
        trade_order = TradeOrder(
            stock_bid_id=bid.id,
            stock_lot_id=stock_lot.id,
            buyer_id=bid.buyer_id,
            farmer_id=stock_lot.farmer_id,
            allocated_quantity_quintals=allocated_qty,
            agreed_price_per_quintal=bid.offered_price_per_quintal,
            status=TradeOrderStatus.CREATED,
        )
        db.add(trade_order)

    db.commit()
    db.refresh(bid)
    db.refresh(stock_lot)

    logger.info(
        f"Farmer {current_user.id} accepted StockBid {bid.id} for {allocated_qty} Q. Remaining stock on Lot {stock_lot.id}: {stock_lot.available_quantity_quintals} Q ({stock_lot.status.value})"
    )

    return _build_stock_bid_response(bid, db)


@router.post(
    "/stock-bids/{bid_id}/reject",
    response_model=StockBidResponse,
    summary="Reject a SUBMITTED post-harvest stock bid",
)
def reject_stock_bid(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock bid {bid_id} not found",
        )

    stock_lot = bid.stock_lot
    if not stock_lot or stock_lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this stock lot",
        )

    if bid.status != StockBidStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject bid in status {bid.status.value}",
        )

    bid.status = StockBidStatus.REJECTED
    db.commit()
    db.refresh(bid)

    return _build_stock_bid_response(bid, db)


# ==========================================
# POST-HARVEST STOCK BID CONTACT SHARING
# ==========================================

@router.post(
    "/stock-bids/{bid_id}/contact-sharing/consent",
    response_model=ContactSharingResponse,
    summary="Submit mutual contact sharing consent for an accepted StockBid",
)
def consent_stock_bid_contact_sharing(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Stock bid {bid_id} not found",
        )

    if bid.status != StockBidStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact sharing consent is only available for ACCEPTED stock bids",
        )

    sharing = (
        db.query(ContactSharing)
        .filter(ContactSharing.stock_bid_id == bid_id)
        .with_for_update()
        .first()
    )
    if not sharing:
        sharing = ContactSharing(
            stock_bid_id=bid.id,
            farmer_id=bid.stock_lot.farmer_id,
            buyer_id=bid.buyer_id,
            farmer_consented=False,
            buyer_consented=False,
            status=ContactSharingStatus.PENDING,
        )
        db.add(sharing)
        db.flush()

    is_farmer = current_user.id == sharing.farmer_id
    is_buyer = current_user.id == sharing.buyer_id

    if not is_farmer and not is_buyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this stock bid contact sharing record",
        )

    from datetime import datetime
    if is_farmer:
        sharing.farmer_consented = True
        sharing.farmer_consented_at = datetime.utcnow()
    if is_buyer:
        sharing.buyer_consented = True
        sharing.buyer_consented_at = datetime.utcnow()

    if sharing.farmer_consented and sharing.buyer_consented:
        sharing.status = ContactSharingStatus.MUTUAL_CONSENT

    db.commit()
    db.refresh(sharing)

    return _build_stock_bid_contact_sharing_response(sharing, current_user.id, db)


@router.post(
    "/stock-bids/{bid_id}/contact-sharing/revoke",
    response_model=ContactSharingResponse,
    summary="Revoke consent for post-harvest stock bid contact sharing",
)
def revoke_stock_bid_contact_sharing(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sharing = (
        db.query(ContactSharing)
        .filter(ContactSharing.stock_bid_id == bid_id)
        .with_for_update()
        .first()
    )
    if not sharing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact sharing record for stock bid {bid_id} not found",
        )

    is_farmer = current_user.id == sharing.farmer_id
    is_buyer = current_user.id == sharing.buyer_id

    if not is_farmer and not is_buyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this contact sharing record",
        )

    if is_farmer:
        sharing.farmer_consented = False
    if is_buyer:
        sharing.buyer_consented = False

    sharing.status = ContactSharingStatus.REVOKED
    db.commit()
    db.refresh(sharing)

    return _build_stock_bid_contact_sharing_response(sharing, current_user.id, db)


@router.get(
    "/stock-bids/{bid_id}/contact-sharing",
    response_model=ContactSharingResponse,
    summary="Get contact sharing status for an accepted StockBid",
)
def get_stock_bid_contact_sharing(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sharing = db.query(ContactSharing).filter(ContactSharing.stock_bid_id == bid_id).first()
    if not sharing:
        bid = db.query(StockBid).filter(StockBid.id == bid_id).first()
        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock bid {bid_id} not found",
            )
        if current_user.id not in (bid.stock_lot.farmer_id, bid.buyer_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not a party to this stock bid",
            )
        return ContactSharingResponse(
            id=0,
            bid_id=bid.id,
            status=ContactSharingStatus.PENDING,
            farmer_consented=False,
            buyer_consented=False,
            created_at=bid.created_at,
            updated_at=bid.updated_at,
            farmer_contact=None,
            buyer_contact=None,
        )

    if current_user.id not in (sharing.farmer_id, sharing.buyer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a party to this contact sharing record",
        )

    return _build_stock_bid_contact_sharing_response(sharing, current_user.id, db)


def _build_stock_bid_contact_sharing_response(
    sharing: ContactSharing, calling_user_id: int, db: Session
) -> ContactSharingResponse:
    farmer_contact = None
    buyer_contact = None

    if sharing.status == ContactSharingStatus.MUTUAL_CONSENT:
        farmer_user = sharing.farmer
        buyer_user = sharing.buyer

        if farmer_user:
            farm_district = None
            farm_state = None
            if farmer_user.farms:
                farm_district = farmer_user.farms[0].district
                farm_state = farmer_user.farms[0].state

            farmer_contact = ContactDetails(
                full_name=farmer_user.full_name or f"Farmer #{farmer_user.id}",
                phone=farmer_user.phone or "N/A",
                email=farmer_user.email or "N/A",
                district=farm_district,
                state=farm_state,
            )

        if buyer_user:
            buyer_contact = ContactDetails(
                full_name=buyer_user.full_name or f"Buyer #{buyer_user.id}",
                phone=buyer_user.phone or "N/A",
                email=buyer_user.email or "N/A",
                business_name=f"Procurement Unit #{buyer_user.id}",
            )

    return ContactSharingResponse(
        id=sharing.id,
        bid_id=sharing.stock_bid_id or sharing.bid_id or 0,
        status=sharing.status,
        farmer_consented=sharing.farmer_consented,
        farmer_consented_at=sharing.farmer_consented_at,
        buyer_consented=sharing.buyer_consented,
        buyer_consented_at=sharing.buyer_consented_at,
        created_at=sharing.created_at,
        updated_at=sharing.updated_at,
        farmer_contact=farmer_contact,
        buyer_contact=buyer_contact,
    )
