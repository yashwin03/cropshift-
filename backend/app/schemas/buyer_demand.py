"""Pydantic schemas for Buyer Demand validation and serialization."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from ..models.buyer_demand import BuyerDemandStatus


class BuyerDemandBase(BaseModel):
    crop_id: int
    variety: Optional[str] = None
    quantity_quintals: float = Field(..., gt=0, description="Quantity required in Quintals (must be > 0)")
    target_price_per_quintal: float = Field(..., gt=0, description="Target buying price per Quintal (must be > 0)")
    delivery_district: str = Field(..., min_length=1)
    delivery_state: Optional[str] = None
    delivery_market_id: Optional[int] = None
    expected_harvest_start: Optional[date] = None
    expected_harvest_end: Optional[date] = None
    quality_grade: Optional[str] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.expected_harvest_start and self.expected_harvest_end:
            if self.expected_harvest_start > self.expected_harvest_end:
                raise ValueError("expected_harvest_start must be before or equal to expected_harvest_end")
        return self


class BuyerDemandCreate(BuyerDemandBase):
    pass


class BuyerDemandUpdate(BaseModel):
    crop_id: Optional[int] = None
    variety: Optional[str] = None
    quantity_quintals: Optional[float] = Field(None, gt=0)
    target_price_per_quintal: Optional[float] = Field(None, gt=0)
    delivery_district: Optional[str] = None
    delivery_state: Optional[str] = None
    delivery_market_id: Optional[int] = None
    expected_harvest_start: Optional[date] = None
    expected_harvest_end: Optional[date] = None
    quality_grade: Optional[str] = None
    status: Optional[BuyerDemandStatus] = None

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.expected_harvest_start and self.expected_harvest_end:
            if self.expected_harvest_start > self.expected_harvest_end:
                raise ValueError("expected_harvest_start must be before or equal to expected_harvest_end")
        return self


class BuyerDemandResponse(BuyerDemandBase):
    id: int
    buyer_id: int
    status: BuyerDemandStatus
    created_at: datetime
    updated_at: datetime
    crop_name: Optional[str] = None
    delivery_market_name: Optional[str] = None
    buyer_company_name: Optional[str] = None

    class Config:
        from_attributes = True


class BuyerDemandFarmerView(BaseModel):
    id: int
    crop_id: int
    crop_name: Optional[str] = None
    variety: Optional[str] = None
    quantity_quintals: float
    target_price_per_quintal: float
    delivery_district: str
    delivery_state: Optional[str] = None
    delivery_market_name: Optional[str] = None
    expected_harvest_start: Optional[date] = None
    expected_harvest_end: Optional[date] = None
    quality_grade: Optional[str] = None
    status: BuyerDemandStatus
    posted_date: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        from_attributes = True
