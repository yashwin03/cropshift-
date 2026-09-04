"""Pydantic schemas for TradeOrder."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from ..models.trade_order import TradeOrderStatus, TradeOrderCancellationReason


class TradeOrderCancelRequest(BaseModel):
    cancellation_reason: Optional[TradeOrderCancellationReason] = Field(
        None, description="Optional controlled cancellation reason"
    )


class TradeOrderResponse(BaseModel):
    id: int
    stock_bid_id: Optional[int] = None
    stock_lot_id: Optional[int] = None
    bid_id: Optional[int] = None
    future_crop_lot_id: Optional[int] = None
    buyer_id: int
    farmer_id: int
    allocated_quantity_quintals: float
    agreed_price_per_quintal: float
    status: TradeOrderStatus
    cancellation_reason: Optional[TradeOrderCancellationReason] = None
    created_at: datetime
    updated_at: datetime
    fulfilled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    crop_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    buyer_display_id: Optional[str] = None
    farmer_display_id: Optional[str] = None
    contact_sharing_status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
