"""Bids API router for pre-sowing indicative bidding."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User, UserRole
from ...models.future_crop_lot import FutureCropLot, FutureCropLotStatus
from ...models.bid import Bid, BidStatus
from ...models.contact_sharing import ContactSharing, ContactSharingStatus
from ...schemas.bid import BidCreate, BidResponse
from ...services.effective_offer_service import compute_effective_offer
from .auth import get_current_user, require_role

router = APIRouter()


def _enrich_bid_response(db: Session, bid: Bid) -> BidResponse:
    res = BidResponse.model_validate(bid)
    if bid.lot:
        if bid.lot.crop:
            res.crop_name = bid.lot.crop.name
        if bid.lot.farm:
            res.district = bid.lot.farm.district
    res.buyer_display_id = f"Buyer #{bid.buyer_id}"

    eff_price, eff_note = compute_effective_offer(db, bid)
    res.effective_offer_per_quintal = eff_price
    res.effective_offer_note = eff_note
    return res


@router.post("/bids", response_model=BidResponse, status_code=status.HTTP_201_CREATED)
def create_bid(
    payload: BidCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Submit an indicative pre-sowing bid on an OPEN Future Crop Lot (BUYER role required)."""
    # 1. Verify Future Crop Lot exists
    lot = db.query(FutureCropLot).filter(FutureCropLot.id == payload.future_crop_lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {payload.future_crop_lot_id} not found."
        )

    # 2. Verify lot status is OPEN
    if lot.status != FutureCropLotStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit bid on future crop lot with status '{lot.status.value}'."
        )

    # 3. Verify quantity rule: bid quantity <= expected lot quantity
    if payload.quantity_quintals > lot.expected_quantity_quintals:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bidded quantity ({payload.quantity_quintals} Q) exceeds total planned lot yield ({lot.expected_quantity_quintals} Q)."
        )

    # 4. Create Bid with derived buyer_id
    bid = Bid(
        future_crop_lot_id=payload.future_crop_lot_id,
        buyer_id=current_user.id,
        offered_price_per_quintal=payload.offered_price_per_quintal,
        quantity_quintals=payload.quantity_quintals,
        conditions=payload.conditions,
        status=BidStatus.SUBMITTED,
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return _enrich_bid_response(db, bid)


@router.get("/bids/me", response_model=List[BidResponse])
def get_my_bids(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """List all indicative bids submitted by the current authenticated buyer."""
    bids = (
        db.query(Bid)
        .filter(Bid.buyer_id == current_user.id)
        .order_by(Bid.created_at.desc())
        .all()
    )
    return [_enrich_bid_response(db, b) for b in bids]


@router.get("/farmer/future-crop-lots/{lot_id}/bids", response_model=List[BidResponse])
def get_bids_for_farmer_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """List all bids submitted for a specific Future Crop Lot (Farmer Owner only)."""
    lot = db.query(FutureCropLot).filter(FutureCropLot.id == lot_id).first()
    if not lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Future crop lot {lot_id} not found."
        )
    if lot.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access permission to inspect bids for this lot."
        )

    bids = (
        db.query(Bid)
        .filter(Bid.future_crop_lot_id == lot_id)
        .order_by(Bid.created_at.desc())
        .all()
    )
    return [_enrich_bid_response(db, b) for b in bids]


@router.post("/bids/{bid_id}/withdraw", response_model=BidResponse)
def withdraw_bid(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.BUYER)),
):
    """Withdraw a submitted bid (Buyer Owner only, status SUBMITTED)."""
    bid = db.query(Bid).filter(Bid.id == bid_id).first()
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bid {bid_id} not found."
        )
    if bid.buyer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to withdraw this bid."
        )
    if bid.status != BidStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw bid in status '{bid.status.value}'."
        )

    bid.status = BidStatus.WITHDRAWN
    db.commit()
    db.refresh(bid)
    return _enrich_bid_response(db, bid)


@router.post("/bids/{bid_id}/accept", response_model=BidResponse)
def accept_bid(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.FARMER)),
):
    """Accept an indicative offer (Farmer Owner only, transactionally safe)."""
    # Transactional state checks
    with db.begin_nested():
        bid = db.query(Bid).filter(Bid.id == bid_id).with_for_update().first()
        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bid {bid_id} not found."
            )

        lot = db.query(FutureCropLot).filter(FutureCropLot.id == bid.future_crop_lot_id).with_for_update().first()
        if not lot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Linked future crop lot not found."
            )

        if lot.farmer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to accept bids on this lot."
            )

        if lot.status != FutureCropLotStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Future crop lot is no longer open (current status: '{lot.status.value}')."
            )

        if bid.status != BidStatus.SUBMITTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot accept bid in status '{bid.status.value}'."
            )

        # Update target bid and parent lot status
        bid.status = BidStatus.ACCEPTED
        lot.status = FutureCropLotStatus.INDICATIVE_ACCEPTED

        # Reject all competing SUBMITTED bids on this lot
        competing_bids = (
            db.query(Bid)
            .filter(
                Bid.future_crop_lot_id == lot.id,
                Bid.id != bid.id,
                Bid.status == BidStatus.SUBMITTED
            )
            .all()
        )
        for comp in competing_bids:
            comp.status = BidStatus.REJECTED

        # Create ContactSharing record in PENDING state
        existing_sharing = db.query(ContactSharing).filter(ContactSharing.bid_id == bid.id).first()
        if not existing_sharing:
            contact_sharing = ContactSharing(
                bid_id=bid.id,
                farmer_id=lot.farmer_id,
                buyer_id=bid.buyer_id,
                farmer_consented=False,
                buyer_consented=False,
                status=ContactSharingStatus.PENDING,
            )
            db.add(contact_sharing)

    db.commit()
    db.refresh(bid)
    return _enrich_bid_response(db, bid)
