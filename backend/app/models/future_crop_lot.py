"""FutureCropLot model for planned agricultural production lots."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class FutureCropLotStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    INDICATIVE_ACCEPTED = "INDICATIVE_ACCEPTED"
    CANCELLED = "CANCELLED"
    HARVESTED = "HARVESTED"
    EXPIRED = "EXPIRED"


class FutureCropLot(Base):
    __tablename__ = "future_crop_lot"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farm.id"), nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False, index=True)
    demand_id = Column(Integer, ForeignKey("buyer_demand.id"), nullable=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendation.id"), nullable=True, index=True)
    cultivation_record_id = Column(Integer, ForeignKey("crop_cultivation_record.id"), nullable=True, index=True)

    variety = Column(String, nullable=True)
    planned_acres = Column(Float, nullable=False)
    expected_quantity_quintals = Column(Float, nullable=False)
    asking_price_per_quintal = Column(Float, nullable=True)
    planned_sowing_date = Column(Date, nullable=False)
    expected_harvest_start = Column(Date, nullable=False, index=True)
    expected_harvest_end = Column(Date, nullable=False)
    quality_grade = Column(String, nullable=True)

    status = Column(Enum(FutureCropLotStatus), nullable=False, default=FutureCropLotStatus.DRAFT, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    farm = relationship("Farm")
    farmer = relationship("User")
    crop = relationship("Crop")
    demand = relationship("BuyerDemand")
    recommendation = relationship("Recommendation")
    cultivation_record = relationship("CropCultivationRecord", back_populates="future_crop_lots")
