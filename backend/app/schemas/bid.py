"""Pydantic schemas for Bid validation and serialization."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from ..models.bid import BidStatus


class BidBase(BaseModel):
    future_crop_lot_id: int
    offered_price_per_quintal: float = Field(..., gt=0, description="Indicative offered price per Quintal (must be > 0)")
    quantity_quintals: float = Field(..., gt=0, description="Bidded quantity in Quintals (must be > 0)")
    conditions: Optional[str] = Field(None, description="Optional quality or delivery conditions")


class BidCreate(BidBase):
    pass


class BidResponse(BidBase):
    id: int
    buyer_id: int
    status: BidStatus
    created_at: datetime
    updated_at: datetime
    
    crop_name: Optional[str] = None
    district: Optional[str] = None
    buyer_display_id: Optional[str] = None
    effective_offer_per_quintal: Optional[float] = None
    effective_offer_note: Optional[str] = None

    class Config:
        from_attributes = True
