"""Pydantic schemas for StockLot validation and responses."""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

from ..models.stock_lot import StockLotStatus


class HarvestRequest(BaseModel):
    actual_quantity_quintals: float = Field(..., gt=0, description="Actual harvested quantity in quintals")
    actual_harvest_date: date = Field(..., description="Actual harvest date")
    quality_grade: Optional[str] = Field(None, description="Quality grade (e.g. Grade A, FAQ)")
    asking_price_per_quintal: Optional[float] = Field(None, gt=0, description="Asking price in ₹/quintal")


class StockLotCreate(BaseModel):
    farm_id: int = Field(..., description="Farm ID")
    crop_id: int = Field(..., description="Crop ID")
    actual_quantity_quintals: float = Field(..., gt=0, description="Actual harvested quantity in quintals")
    actual_harvest_date: date = Field(..., description="Actual harvest date")
    variety: Optional[str] = Field(None, description="Crop variety")
    quality_grade: Optional[str] = Field(None, description="Quality grade")
    asking_price_per_quintal: Optional[float] = Field(None, gt=0, description="Asking price in ₹/quintal")


class StockLotUpdate(BaseModel):
    actual_quantity_quintals: Optional[float] = Field(None, gt=0)
    actual_harvest_date: Optional[date] = None
    variety: Optional[str] = None
    quality_grade: Optional[str] = None
    asking_price_per_quintal: Optional[float] = Field(None, gt=0)


class StockLotResponse(BaseModel):
    id: int
    farmer_id: int
    farm_id: int
    future_crop_lot_id: Optional[int] = None
    crop_id: int
    variety: Optional[str] = None
    actual_quantity_quintals: float
    available_quantity_quintals: float
    actual_harvest_date: date
    quality_grade: Optional[str] = None
    asking_price_per_quintal: Optional[float] = None
    quality_cert_filename: Optional[str] = None
    quality_cert_url: Optional[str] = None
    quality_cert_uploaded_at: Optional[datetime] = None
    status: StockLotStatus
    created_at: datetime
    updated_at: datetime

    # Expanded metadata
    crop_name: Optional[str] = None
    farm_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class StockLotMarketplaceView(BaseModel):
    id: int
    crop_id: int
    crop_name: Optional[str] = None
    variety: Optional[str] = None
    actual_available_quantity: float = Field(..., alias="available_quantity_quintals")
    available_quantity_quintals: float
    actual_harvest_date: date
    quality_grade: Optional[str] = None
    asking_price_per_quintal: Optional[float] = None
    quality_cert_filename: Optional[str] = None
    quality_cert_url: Optional[str] = None
    quality_cert_uploaded_at: Optional[datetime] = None
    district: Optional[str] = None
    state: Optional[str] = None
    status: StockLotStatus

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
