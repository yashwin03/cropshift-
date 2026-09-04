"""TradeOrder model for post-harvest trade fulfillment tracking."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class TradeOrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class TradeOrderCancellationReason(str, enum.Enum):
    BUYER_CANCELLED = "BUYER_CANCELLED"
    FARMER_CANCELLED = "FARMER_CANCELLED"
    QUALITY_ISSUE = "QUALITY_ISSUE"
    NO_SHOW = "NO_SHOW"
    OTHER = "OTHER"


class TradeOrder(Base):
    __tablename__ = "trade_order"

    id = Column(Integer, primary_key=True, index=True)
    stock_bid_id = Column(Integer, ForeignKey("stock_bid.id"), nullable=False, unique=True, index=True)
    stock_lot_id = Column(Integer, ForeignKey("stock_lot.id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    allocated_quantity_quintals = Column(Float, nullable=False)
    agreed_price_per_quintal = Column(Float, nullable=False)

    status = Column(Enum(TradeOrderStatus), nullable=False, default=TradeOrderStatus.CREATED, index=True)
    cancellation_reason = Column(Enum(TradeOrderCancellationReason), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    fulfilled_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    # Relationships
    stock_bid = relationship("StockBid")
    stock_lot = relationship("StockLot")
    buyer = relationship("User", foreign_keys=[buyer_id])
    farmer = relationship("User", foreign_keys=[farmer_id])
