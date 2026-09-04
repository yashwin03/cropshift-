"""StockBid model for post-harvest physical stock bidding."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class StockBidStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class StockBid(Base):
    __tablename__ = "stock_bid"

    id = Column(Integer, primary_key=True, index=True)
    stock_lot_id = Column(Integer, ForeignKey("stock_lot.id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    offered_price_per_quintal = Column(Float, nullable=False)
    requested_quantity_quintals = Column(Float, nullable=False)
    allocated_quantity_quintals = Column(Float, nullable=False, default=0.0)
    conditions = Column(String, nullable=True)

    status = Column(Enum(StockBidStatus), nullable=False, default=StockBidStatus.SUBMITTED, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    stock_lot = relationship("StockLot")
    buyer = relationship("User")
