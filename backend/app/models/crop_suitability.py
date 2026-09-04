"""CropSuitability model -- A1 spec entity."""
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class CropSuitability(Base):
    __tablename__ = "crop_suitability"

    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    region = Column(String, nullable=False)              # district or region name
    soil_type = Column(String, nullable=True)            # e.g. "red laterite"
    water_requirement_level = Column(String, nullable=True)  # HIGH / MEDIUM / LOW
    suitability_base_score = Column(Float, nullable=False)   # 0-100
    notes = Column(String, nullable=True)

    # Relationships
    crop = relationship("Crop", back_populates="suitabilities")
