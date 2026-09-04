"""Pydantic schemas for Future Crop Lot validation and serialization."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from ..models.future_crop_lot import FutureCropLotStatus


class FutureCropLotBase(BaseModel):
    farm_id: int
    crop_id: int
    demand_id: Optional[int] = None
    recommendation_id: Optional[int] = None
    variety: Optional[str] = None
    planned_acres: float = Field(..., gt=0, description="Acres committed (must be > 0)")
    expected_quantity_quintals: float = Field(..., gt=0, description="Expected yield in Quintals (must be > 0)")
    asking_price_per_quintal: Optional[float] = Field(None, gt=0, description="Indicative asking price per Quintal")
    planned_sowing_date: date
    expected_harvest_start: date
    expected_harvest_end: date
    quality_grade: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expected_harvest_start > self.expected_harvest_end:
            raise ValueError("expected_harvest_start must be before or equal to expected_harvest_end")
        if self.planned_sowing_date > self.expected_harvest_start:
            raise ValueError("planned_sowing_date must be before or equal to expected_harvest_start")
        return self


class FutureCropLotCreate(FutureCropLotBase):
    status: Optional[FutureCropLotStatus] = FutureCropLotStatus.DRAFT


class FutureCropLotUpdate(BaseModel):
    farm_id: Optional[int] = None
    crop_id: Optional[int] = None
    demand_id: Optional[int] = None
    recommendation_id: Optional[int] = None
    variety: Optional[str] = None
    planned_acres: Optional[float] = Field(None, gt=0)
    expected_quantity_quintals: Optional[float] = Field(None, gt=0)
    asking_price_per_quintal: Optional[float] = Field(None, gt=0)
    planned_sowing_date: Optional[date] = None
    expected_harvest_start: Optional[date] = None
    expected_harvest_end: Optional[date] = None
    quality_grade: Optional[str] = None
    status: Optional[FutureCropLotStatus] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.expected_harvest_start and self.expected_harvest_end:
            if self.expected_harvest_start > self.expected_harvest_end:
                raise ValueError("expected_harvest_start must be before or equal to expected_harvest_end")
        if self.planned_sowing_date and self.expected_harvest_start:
            if self.planned_sowing_date > self.expected_harvest_start:
                raise ValueError("planned_sowing_date must be before or equal to expected_harvest_start")
        return self


class FutureCropLotResponse(FutureCropLotBase):
    id: int
    farmer_id: int
    status: FutureCropLotStatus
    created_at: datetime
    updated_at: datetime
    farm_name: Optional[str] = None
    crop_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    demand_title: Optional[str] = None

    class Config:
        from_attributes = True


class FutureCropLotMarketplaceView(BaseModel):
    id: int
    crop_id: int
    crop_name: Optional[str] = None
    variety: Optional[str] = None
    planned_acres: float
    expected_quantity_quintals: float
    asking_price_per_quintal: Optional[float] = None
    expected_harvest_start: date
    expected_harvest_end: date
    quality_grade: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    status: FutureCropLotStatus
    demand_id: Optional[int] = None
    demand_title: Optional[str] = None
    farmer_display_id: Optional[str] = None

    class Config:
        from_attributes = True
