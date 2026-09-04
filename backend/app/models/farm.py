"""Farm model -- A1 spec entity."""
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..database.base import Base


class Farm(Base):
    __tablename__ = "farm"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("farmer.id"), nullable=False)
    land_area_acre = Column(Float, nullable=False)
    water_availability = Column(Boolean, nullable=False, default=True)
    soil_type = Column(String, nullable=True)       # e.g. "red laterite", "black cotton"
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    current_crop_id = Column(Integer, ForeignKey("crop.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=True)

    # Relationships
    farmer = relationship("Farmer", back_populates="farms")
    owner = relationship("User", back_populates="farms")
    current_crop = relationship("Crop", back_populates="farms")
    recommendations = relationship("Recommendation", back_populates="farm")
