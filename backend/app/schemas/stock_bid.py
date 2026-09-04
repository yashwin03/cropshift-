from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from ..models.stock_bid import StockBidStatus


class StockBidCreate(BaseModel):
    offered_price_per_quintal: float = Field(..., gt=0, description="Offered price in ₹ per quintal")
    requested_quantity_quintals: float = Field(..., gt=0, description="Requested quantity in quintals")
    conditions: Optional[str] = Field(None, max_length=500, description="Optional quality/delivery terms")


class StockBidAcceptRequest(BaseModel):
    allocated_quantity_quintals: float = Field(..., gt=0, description="Allocated quantity in quintals")


class StockBidResponse(BaseModel):
    id: int
    stock_lot_id: int
    buyer_id: int
    offered_price_per_quintal: float
    requested_quantity_quintals: float
    allocated_quantity_quintals: float
    conditions: Optional[str] = None
    status: StockBidStatus
    created_at: datetime
    updated_at: datetime

    crop_name: Optional[str] = None
    district: Optional[str] = None
    buyer_display_id: Optional[str] = None
    effective_offer_per_quintal: Optional[float] = None
    effective_offer_note: Optional[str] = None

    class Config:
        from_attributes = True


class StockBidFarmerView(BaseModel):
    id: int
    stock_lot_id: int
    buyer_display_id: str
    offered_price_per_quintal: float
    requested_quantity_quintals: float
    allocated_quantity_quintals: float
    conditions: Optional[str] = None
    status: StockBidStatus
    effective_offer_per_quintal: Optional[float] = None
    effective_offer_note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
