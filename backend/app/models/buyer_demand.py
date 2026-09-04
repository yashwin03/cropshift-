"""BuyerDemand model for Commercial Buyer procurement requirements."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class BuyerDemandStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class BuyerDemand(Base):
    __tablename__ = "buyer_demand"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False, index=True)
    variety = Column(String, nullable=True)
    quantity_quintals = Column(Float, nullable=False)
    target_price_per_quintal = Column(Float, nullable=False)
    delivery_district = Column(String, nullable=False, index=True)
    delivery_state = Column(String, nullable=True)
    delivery_market_id = Column(Integer, ForeignKey("market.id"), nullable=True)
    expected_harvest_start = Column(Date, nullable=True)
    expected_harvest_end = Column(Date, nullable=True)
    quality_grade = Column(String, nullable=True)
    status = Column(Enum(BuyerDemandStatus), nullable=False, default=BuyerDemandStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    buyer = relationship("User")
    crop = relationship("Crop")
    delivery_market = relationship("Market")
