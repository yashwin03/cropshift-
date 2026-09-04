"""Recommendation model -- A1 spec entity."""
import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendation"

    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farm.id"), nullable=False)
    recommended_crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)

    # Component scores (0-100)
    suitability_score = Column(Float, nullable=True)
    profitability_score = Column(Float, nullable=True)
    market_score = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    safety_score = Column(Float, nullable=True)

    # Decision: SWITCH / CAUTION / DONT_SWITCH
    decision = Column(String, nullable=False)

    # Profitability summary (INR/acre)
    expected_profit = Column(Float, nullable=True)
    current_crop_profit = Column(Float, nullable=True)
    profit_difference = Column(Float, nullable=True)

    # Explainability
    reasons = Column(JSON, nullable=True)   # list of reason strings
    risks = Column(JSON, nullable=True)     # list of risk strings

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="recommendations")
    recommended_crop = relationship("Crop")
