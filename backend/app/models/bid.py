"""Bid model for pre-sowing indicative bidding."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class BidStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class Bid(Base):
    __tablename__ = "bid"

    id = Column(Integer, primary_key=True, index=True)
    future_crop_lot_id = Column(Integer, ForeignKey("future_crop_lot.id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    offered_price_per_quintal = Column(Float, nullable=False)
    quantity_quintals = Column(Float, nullable=False)
    conditions = Column(String, nullable=True)

    status = Column(Enum(BidStatus), nullable=False, default=BidStatus.SUBMITTED, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    lot = relationship("FutureCropLot")
    buyer = relationship("User")
