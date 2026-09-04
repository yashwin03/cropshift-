"""TradeOrder API endpoints for post-harvest trade fulfillment tracking."""
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...models.user import User, UserRole
from ...models.stock_lot import StockLot, StockLotStatus
from ...models.stock_bid import StockBid, StockBidStatus
from ...models.contact_sharing import ContactSharing, ContactSharingStatus
from ...models.trade_order import TradeOrder, TradeOrderStatus, TradeOrderCancellationReason
from ...schemas.trade_order import TradeOrderResponse, TradeOrderCancelRequest
from .auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


def _build_trade_order_response(order: TradeOrder, db: Session) -> TradeOrderResponse:
    stock_lot = order.stock_lot
    future_lot = order.future_crop_lot
    
    crop_name = None
    district = None
    state = None
    
    if stock_lot:
        crop_name = stock_lot.crop.name if stock_lot.crop else None
        district = stock_lot.farm.district if stock_lot.farm else None
        state = stock_lot.farm.state if stock_lot.farm else None
    elif future_lot:
        crop_name = future_lot.crop.name if future_lot.crop else None
        district = future_lot.farm.district if future_lot.farm else None
        state = future_lot.farm.state if future_lot.farm else None

    buyer_display_id = f"Buyer #{order.buyer_id}"
    if order.buyer and (order.buyer.full_name or order.buyer.username):
        buyer_display_id = order.buyer.full_name or order.buyer.username

    farmer_display_id = f"Farmer #{order.farmer_id}"
    if order.farmer and (order.farmer.full_name or order.farmer.username):
        farmer_display_id = order.farmer.full_name or order.farmer.username

    contact_sharing_status = "NOT_CREATED"
    if order.stock_bid_id:
        sharing = (
            db.query(ContactSharing)
            .filter(ContactSharing.stock_bid_id == order.stock_bid_id)
            .first()
        )
    elif order.bid_id:
        sharing = (
            db.query(ContactSharing)
            .filter(ContactSharing.bid_id == order.bid_id)
            .first()
        )
    else:
        sharing = None

    if sharing:
        contact_sharing_status = sharing.status.value

    return TradeOrderResponse(
        id=order.id,
        stock_bid_id=order.stock_bid_id,
        stock_lot_id=order.stock_lot_id,
        bid_id=order.bid_id,
        future_crop_lot_id=order.future_crop_lot_id,
        buyer_id=order.buyer_id,
        farmer_id=order.farmer_id,
        allocated_quantity_quintals=order.allocated_quantity_quintals,
        agreed_price_per_quintal=order.agreed_price_per_quintal,
        status=order.status,
        cancellation_reason=order.cancellation_reason,
        created_at=order.created_at,
        updated_at=order.updated_at,
        fulfilled_at=order.fulfilled_at,
        cancelled_at=order.cancelled_at,
        crop_name=crop_name,
        district=district,
        state=state,
        buyer_display_id=buyer_display_id,
        farmer_display_id=farmer_display_id,
        contact_sharing_status=contact_sharing_status,
    )


@router.get(
    "/trade-orders/me",
    response_model=List[TradeOrderResponse],
    summary="Get my Trade Orders",
    description="Retrieve TradeOrders where the current user is either the buyer or the farmer.",
)
def get_my_trade_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    orders = (
        db.query(TradeOrder)
        .filter((TradeOrder.buyer_id == current_user.id) | (TradeOrder.farmer_id == current_user.id))
        .order_by(TradeOrder.created_at.desc())
        .all()
    )
    return [_build_trade_order_response(o, db) for o in orders]


@router.get(
    "/trade-orders/{order_id}",
    response_model=TradeOrderResponse,
    summary="Get Trade Order details by ID",
    description="Retrieve details for a specific TradeOrder. Requires user to be buyer or farmer.",
)
def get_trade_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(TradeOrder).filter(TradeOrder.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade order {order_id} not found",
        )

    if current_user.id != order.buyer_id and current_user.id != order.farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this trade order",
        )

    return _build_trade_order_response(order, db)


@router.post(
    "/trade-orders/{order_id}/fulfill",
    response_model=TradeOrderResponse,
    summary="Mark Trade Order as FULFILLED",
    description="Participant (buyer or farmer) marks the trade order as fulfilled.",
)
def fulfill_trade_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(TradeOrder).filter(TradeOrder.id == order_id).with_for_update().first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade order {order_id} not found",
        )

    if current_user.id != order.buyer_id and current_user.id != order.farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to fulfill this trade order",
        )

    if order.status == TradeOrderStatus.FULFILLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trade order is already fulfilled",
        )

    if order.status == TradeOrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelled trade order cannot be fulfilled",
        )

    if order.status != TradeOrderStatus.CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade order in status {order.status.value} cannot be fulfilled",
        )

    order.status = TradeOrderStatus.FULFILLED
    order.fulfilled_at = datetime.utcnow()

    db.commit()
    db.refresh(order)

    logger.info(f"User {current_user.id} marked TradeOrder {order_id} as FULFILLED.")
    return _build_trade_order_response(order, db)


@router.post(
    "/trade-orders/{order_id}/cancel",
    response_model=TradeOrderResponse,
    summary="Cancel Trade Order & restore stock quantity",
    description="Cancel a CREATED TradeOrder and return allocated quantity back to StockLot.",
)
def cancel_trade_order(
    order_id: int,
    payload: Optional[TradeOrderCancelRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = db.query(TradeOrder).filter(TradeOrder.id == order_id).with_for_update().first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trade order {order_id} not found",
        )

    if current_user.id != order.buyer_id and current_user.id != order.farmer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this trade order",
        )

    if order.status == TradeOrderStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trade order is already cancelled",
        )

    if order.status == TradeOrderStatus.FULFILLED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fulfilled trade order cannot be cancelled",
        )

    if order.status != TradeOrderStatus.CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Trade order in status {order.status.value} cannot be cancelled",
        )

    # Lock associated StockLot
    stock_lot = (
        db.query(StockLot)
        .filter(StockLot.id == order.stock_lot_id)
        .with_for_update()
        .first()
    )
    if not stock_lot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Associated StockLot {order.stock_lot_id} not found",
        )

    # Determine cancellation reason
    reason = TradeOrderCancellationReason.OTHER
    if payload and payload.cancellation_reason:
        reason = payload.cancellation_reason
    elif current_user.id == order.buyer_id:
        reason = TradeOrderCancellationReason.BUYER_CANCELLED
    elif current_user.id == order.farmer_id:
        reason = TradeOrderCancellationReason.FARMER_CANCELLED

    # Update TradeOrder status
    order.status = TradeOrderStatus.CANCELLED
    order.cancelled_at = datetime.utcnow()
    order.cancellation_reason = reason

    # Restore quantity to StockLot
    new_available = stock_lot.available_quantity_quintals + order.allocated_quantity_quintals
    # Cap available_quantity at actual_quantity
    stock_lot.available_quantity_quintals = min(new_available, stock_lot.actual_quantity_quintals)

    # Recalculate StockLot status
    if stock_lot.available_quantity_quintals == stock_lot.actual_quantity_quintals:
        if stock_lot.status != StockLotStatus.DRAFT:
            stock_lot.status = StockLotStatus.AVAILABLE
    elif stock_lot.available_quantity_quintals > 0:
        stock_lot.status = StockLotStatus.PARTIALLY_SOLD

    db.commit()
    db.refresh(order)
    db.refresh(stock_lot)

    logger.info(
        f"User {current_user.id} cancelled TradeOrder {order_id} (Reason: {reason.value}). Restored {order.allocated_quantity_quintals} Q to StockLot {stock_lot.id} (New available: {stock_lot.available_quantity_quintals} Q, status: {stock_lot.status.value})."
    )

    return _build_trade_order_response(order, db)
