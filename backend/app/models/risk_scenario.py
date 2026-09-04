"""RiskScenario model -- A1 spec entity."""
import enum

from sqlalchemy import Column, Integer, String, Float, Enum

from ..database.base import Base


class RiskCode(str, enum.Enum):
    BASELINE = "BASELINE"
    PRICE_DOWN = "PRICE_DOWN"
    YIELD_DOWN = "YIELD_DOWN"
    WATER_RISK = "WATER_RISK"


class RiskScenario(Base):
    __tablename__ = "risk_scenario"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(Enum(RiskCode), nullable=False, unique=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price_multiplier = Column(Float, nullable=False, default=1.0)   # e.g. 0.8 = 20% price drop
    yield_multiplier = Column(Float, nullable=False, default=1.0)   # e.g. 0.7 = 30% yield drop
    water_penalty = Column(Float, nullable=False, default=0.0)      # score deduction 0-100
