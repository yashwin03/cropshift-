"""Market model -- A1 spec entity."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry

from ..database.base import Base


class Market(Base):
    __tablename__ = "market"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)
    location = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    market_type = Column(String, nullable=True)   # e.g. "APMC", "PRIVATE"

    # Relationships
    prices = relationship("MarketPrice", back_populates="market")
