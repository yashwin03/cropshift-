from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from ..database.base import Base
import enum

class WaterSourceType(enum.Enum):
    RIVER = "river"
    LAKE = "lake"
    WELL = "well"
    PUMP = "pump"

class WaterSource(Base):
    __tablename__ = "water_source"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(Enum(WaterSourceType), nullable=False)
    capacity_liters = Column(Float, nullable=True)
    location = Column(String, nullable=True)  # Could be a POINT geometry, simplified as string for now
    farm_id = Column(Integer, ForeignKey("farm.id"), nullable=True)

    farm = relationship("Farm", back_populates="water_sources")
