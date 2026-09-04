"""CropEconomics model -- A1 spec entity."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class CropEconomics(Base):
    __tablename__ = "crop_economics"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    region = Column(String, nullable=False)             # e.g. "Karnataka"
    expected_yield_per_acre = Column(Float, nullable=False)
    yield_unit = Column(String, nullable=False)         # e.g. "quintal"
    production_cost_per_acre = Column(Float, nullable=False)  # INR
    expected_price_per_unit = Column(Float, nullable=False)   # INR per yield_unit
    data_status = Column(String, nullable=False)         # DEMO / STATIC / ESTIMATED
    data_source = Column(String, nullable=True)

    # Relationships
    crop = relationship("Crop", back_populates="economics")
