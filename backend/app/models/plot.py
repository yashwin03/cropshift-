from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from ..database.base import Base

class Plot(Base):
    __tablename__ = "plot"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farm.id"), nullable=False)
    soil_id = Column(Integer, ForeignKey("soil.id"), nullable=True)
    geometry = Column(Geometry(geometry_type='POLYGON', srid=4326), nullable=False)
    area = Column(Float, nullable=False)  # acres

    farm = relationship("Farm", back_populates="plots")
    soil = relationship("Soil", back_populates="plots")
    crops = relationship("Crop", secondary="crop_calendar", back_populates="plots")
