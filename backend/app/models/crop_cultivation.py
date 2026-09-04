"""
crop_cultivation.py -- Crop Cultivation Record model.
Represents an authoritative record of a farmer's crop cultivation activity.
"""
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database.base import Base


class CultivationStage(str, enum.Enum):
    PLANNED = "PLANNED"
    GROWING = "GROWING"
    READY_FOR_HARVEST = "READY_FOR_HARVEST"
    HARVESTED = "HARVESTED"


class EvidenceStatus(str, enum.Enum):
    FARMER_DECLARED = "FARMER_DECLARED"
    FIELD_EVIDENCE = "FIELD_EVIDENCE"
    VERIFIED = "VERIFIED"


class CropCultivationRecord(Base):
    __tablename__ = "crop_cultivation_record"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    farm_id = Column(Integer, ForeignKey("farm.id"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False, index=True)

    crop_name = Column(String, nullable=False)
    variety = Column(String, nullable=True)
    area_acres = Column(Float, nullable=False, default=1.0)
    cultivation_stage = Column(
        SQLEnum(CultivationStage, native_enum=False),
        nullable=False,
        default=CultivationStage.GROWING,
        index=True
    )

    sowing_date = Column(String, nullable=True)
    expected_harvest_date = Column(String, nullable=True)
    expected_yield_quintals = Column(Float, nullable=True)
    actual_harvest_quantity_quintals = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    evidence_status = Column(
        SQLEnum(EvidenceStatus, native_enum=False),
        nullable=False,
        default=EvidenceStatus.FARMER_DECLARED
    )
    source_type = Column(String, nullable=False, default="CropShift farmer network dataset")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    farmer = relationship("User", back_populates="cultivation_records")
    farm = relationship("Farm")
    crop = relationship("Crop")
    future_crop_lots = relationship("FutureCropLot", back_populates="cultivation_record")
