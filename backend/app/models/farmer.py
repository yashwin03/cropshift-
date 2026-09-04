"""Farmer model -- A1 spec entity."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..database.base import Base


class Farmer(Base):
    __tablename__ = "farmer"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    language = Column(String, nullable=True)   # e.g. "kn", "en", "hi"
    district = Column(String, nullable=True)
    state = Column(String, nullable=True)

    farms = relationship("Farm", back_populates="farmer")
