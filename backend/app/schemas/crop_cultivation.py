"""
crop_cultivation.py -- Pydantic schemas for Crop Cultivation Record API endpoints.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.crop_cultivation import CultivationStage, EvidenceStatus


class CropCultivationCreate(BaseModel):
    farm_id: Optional[int] = None
    crop_id: int
    variety: Optional[str] = None
    area_acres: float = Field(gt=0, default=1.0)
    cultivation_stage: CultivationStage = CultivationStage.GROWING
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    expected_yield_quintals: Optional[float] = None
    notes: Optional[str] = None


class CropCultivationUpdate(BaseModel):
    variety: Optional[str] = None
    area_acres: Optional[float] = Field(gt=0, default=None)
    cultivation_stage: Optional[CultivationStage] = None
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    expected_yield_quintals: Optional[float] = None
    notes: Optional[str] = None


class RecordHarvestPayload(BaseModel):
    actual_harvest_quantity_quintals: float = Field(gt=0)
    notes: Optional[str] = None


class CropCultivationResponse(BaseModel):
    id: int
    farmer_id: int
    farm_id: int
    crop_id: int
    crop_name: str
    variety: Optional[str] = None
    area_acres: float
    cultivation_stage: CultivationStage
    sowing_date: Optional[str] = None
    expected_harvest_date: Optional[str] = None
    expected_yield_quintals: Optional[float] = None
    actual_harvest_quantity_quintals: Optional[float] = None
    notes: Optional[str] = None
    evidence_status: EvidenceStatus
    source_type: str
    created_at: datetime
    updated_at: datetime

    # Location / Farm Metadata
    district: Optional[str] = None
    state: Optional[str] = None

    class Config:
        from_attributes = True
