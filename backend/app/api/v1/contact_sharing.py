"""API Router for Post-Acceptance Mutual Contact Sharing."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User
from ...models.bid import Bid, BidStatus
from ...models.contact_sharing import ContactSharing, ContactSharingStatus
from ...schemas.contact_sharing import ContactSharingResponse, ContactDetails
from .auth import get_current_user

router = APIRouter(prefix="/bids", tags=["Contact Sharing"])


def _build_contact_sharing_response(
    db: Session, sharing: ContactSharing, current_user_id: int
) -> ContactSharingResponse:
    res = ContactSharingResponse.model_validate(sharing)

    # Only expose contact information when MUTUAL_CONSENT status is active
    if sharing.status == ContactSharingStatus.MUTUAL_CONSENT:
        # If the caller is the Buyer, return Farmer's contact details
        if current_user_id == sharing.buyer_id:
            farmer_user = sharing.farmer or db.query(User).filter(User.id == sharing.farmer_id).first()
            if farmer_user:
                district = None
                state = None
                # Retrieve farm district/state if linked to lot
                if sharing.bid and sharing.bid.lot and sharing.bid.lot.farm:
                    district = sharing.bid.lot.farm.district
                    state = sharing.bid.lot.farm.state

                res.farmer_contact = ContactDetails(
                    full_name=farmer_user.full_name or farmer_user.username,
                    phone=farmer_user.phone,
                    email=farmer_user.email,
                    district=district,
                    state=state,
                )

        # If the caller is the Farmer, return Buyer's contact details
        if current_user_id == sharing.farmer_id:
            buyer_user = sharing.buyer or db.query(User).filter(User.id == sharing.buyer_id).first()
            if buyer_user:
                res.buyer_contact = ContactDetails(
                    full_name=buyer_user.full_name or buyer_user.username,
                    phone=buyer_user.phone,
                    email=buyer_user.email,
                    business_name=f"Buyer #{buyer_user.id}",
                )

    return res


@router.post("/{bid_id}/contact-sharing/consent", response_model=ContactSharingResponse)
def consent_contact_sharing(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Grant consent for mutual contact sharing on an accepted bid (Idempotent, Transactionally Safe)."""
    with db.begin_nested():
        sharing = (
            db.query(ContactSharing)
            .filter(ContactSharing.bid_id == bid_id)
            .with_for_update()
            .first()
        )
        if not sharing:
            bid = db.query(Bid).filter(Bid.id == bid_id).first()
            if not bid:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bid {bid_id} not found.",
                )
            if current_user.id != bid.buyer_id and (not bid.lot or current_user.id != bid.lot.farmer_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to grant consent for this bid.",
                )
            if bid.status != BidStatus.ACCEPTED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot grant contact sharing consent for bid in status '{bid.status.value}'. Bid must be ACCEPTED.",
                )
            sharing = ContactSharing(
                bid_id=bid.id,
                farmer_id=bid.lot.farmer_id,
                buyer_id=bid.buyer_id,
                farmer_consented=False,
                buyer_consented=False,
                status=ContactSharingStatus.PENDING,
            )
            db.add(sharing)
            db.flush()

        # Ownership and authorization validation
        if current_user.id == sharing.farmer_id:
            sharing.farmer_consented = True
            if not sharing.farmer_consented_at:
                sharing.farmer_consented_at = datetime.utcnow()
        elif current_user.id == sharing.buyer_id:
            sharing.buyer_consented = True
            if not sharing.buyer_consented_at:
                sharing.buyer_consented_at = datetime.utcnow()
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to grant consent for this bid.",
            )

        # Recalculate mutual consent state
        if sharing.farmer_consented and sharing.buyer_consented:
            sharing.status = ContactSharingStatus.MUTUAL_CONSENT
        else:
            sharing.status = ContactSharingStatus.PENDING

    db.commit()
    db.refresh(sharing)
    return _build_contact_sharing_response(db, sharing, current_user.id)


@router.post("/{bid_id}/contact-sharing/revoke", response_model=ContactSharingResponse)
def revoke_contact_sharing(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke consent for mutual contact sharing on an accepted bid."""
    with db.begin_nested():
        sharing = (
            db.query(ContactSharing)
            .filter(ContactSharing.bid_id == bid_id)
            .with_for_update()
            .first()
        )
        if not sharing:
            bid = db.query(Bid).filter(Bid.id == bid_id).first()
            if not bid:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Bid {bid_id} not found.",
                )
            if current_user.id != bid.buyer_id and (not bid.lot or current_user.id != bid.lot.farmer_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to revoke consent for this bid.",
                )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Contact sharing record for bid {bid_id} not found.",
            )

        if current_user.id == sharing.farmer_id:
            sharing.farmer_consented = False
        elif current_user.id == sharing.buyer_id:
            sharing.buyer_consented = False
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to revoke consent for this bid.",
            )

        sharing.status = ContactSharingStatus.REVOKED

    db.commit()
    db.refresh(sharing)
    return _build_contact_sharing_response(db, sharing, current_user.id)


@router.get("/{bid_id}/contact-sharing", response_model=ContactSharingResponse)
def get_contact_sharing(
    bid_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get contact sharing status and unlocked details (Only Farmer Owner or Buyer Owner)."""
    sharing = db.query(ContactSharing).filter(ContactSharing.bid_id == bid_id).first()
    if not sharing:
        bid = db.query(Bid).filter(Bid.id == bid_id).first()
        if not bid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bid {bid_id} not found.",
            )
        if current_user.id != bid.buyer_id and (not bid.lot or current_user.id != bid.lot.farmer_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to contact sharing for this bid.",
            )
        if bid.status != BidStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contact sharing is only available for ACCEPTED bids.",
            )
        sharing = ContactSharing(
            bid_id=bid.id,
            farmer_id=bid.lot.farmer_id,
            buyer_id=bid.buyer_id,
            farmer_consented=False,
            buyer_consented=False,
            status=ContactSharingStatus.PENDING,
        )
        db.add(sharing)
        db.commit()
        db.refresh(sharing)

    if current_user.id != sharing.farmer_id and current_user.id != sharing.buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to contact sharing for this bid.",
        )

    return _build_contact_sharing_response(db, sharing, current_user.id)
