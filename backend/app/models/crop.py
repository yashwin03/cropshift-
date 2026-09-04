"""Crop model -- A1 spec entity."""
import enum

from sqlalchemy import Column, Integer, String, Float, Boolean, Enum
from sqlalchemy.orm import relationship

from ..database.base import Base


class CropType(str, enum.Enum):
    CEREAL = "CEREAL"
    OILSEED = "OILSEED"
    PULSE = "PULSE"
    OTHER = "OTHER"


class Crop(Base):
    __tablename__ = "crop"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    crop_type = Column(Enum(CropType), nullable=False)
    season = Column(String, nullable=True)          # e.g. "Kharif", "Rabi"
    duration_days = Column(Integer, nullable=True)
    water_requirement = Column(String, nullable=True)  # e.g. "HIGH", "MEDIUM", "LOW"
    is_oilseed = Column(Boolean, nullable=False, default=False)

    # Relationships
    farms = relationship("Farm", back_populates="current_crop")
    economics = relationship("CropEconomics", back_populates="crop")
    suitabilities = relationship("CropSuitability", back_populates="crop")
    market_prices = relationship("MarketPrice", back_populates="crop")
