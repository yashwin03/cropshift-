"""StockLot model for actual physical harvested agricultural inventory."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class StockLotStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    AVAILABLE = "AVAILABLE"
    PARTIALLY_SOLD = "PARTIALLY_SOLD"
    SOLD = "SOLD"
    CANCELLED = "CANCELLED"


class StockLot(Base):
    __tablename__ = "stock_lot"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    farm_id = Column(Integer, ForeignKey("farm.id"), nullable=False, index=True)
    future_crop_lot_id = Column(Integer, ForeignKey("future_crop_lot.id"), nullable=True, index=True)
    cultivation_record_id = Column(Integer, ForeignKey("crop_cultivation_record.id"), nullable=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False, index=True)

    variety = Column(String, nullable=True)
    actual_quantity_quintals = Column(Float, nullable=False)
    available_quantity_quintals = Column(Float, nullable=False)
    actual_harvest_date = Column(Date, nullable=False, index=True)
    quality_grade = Column(String, nullable=True)
    asking_price_per_quintal = Column(Float, nullable=True)

    quality_cert_filename = Column(String, nullable=True)
    quality_cert_url = Column(String, nullable=True)
    quality_cert_uploaded_at = Column(DateTime, nullable=True)

    status = Column(Enum(StockLotStatus), nullable=False, default=StockLotStatus.DRAFT, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    farmer = relationship("User")
    farm = relationship("Farm")
    future_crop_lot = relationship("FutureCropLot")
    cultivation_record = relationship("CropCultivationRecord")
    crop = relationship("Crop")
