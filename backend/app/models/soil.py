from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from ..database.base import Base

class Soil(Base):
    __tablename__ = "soil"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ph = Column(Float, nullable=True)
    texture = Column(String, nullable=True)

    plots = relationship("Plot", back_populates="soil")
