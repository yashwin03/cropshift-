"""MarketPrice model -- A1 spec entity."""
import datetime

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class MarketPrice(Base):
    __tablename__ = "market_price"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("market.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    price = Column(Float, nullable=False)              # INR per yield_unit
    price_unit = Column(String, nullable=False)        # e.g. "quintal"
    price_date = Column(Date, nullable=False)
    trend = Column(String, nullable=True)              # e.g. "STABLE", "RISING", "FALLING"
    data_status = Column(String, nullable=False)       # DEMO / STATIC / ESTIMATED
    data_source = Column(String, nullable=True)

    # Relationships
    market = relationship("Market", back_populates="prices")
    crop = relationship("Crop", back_populates="market_prices")
