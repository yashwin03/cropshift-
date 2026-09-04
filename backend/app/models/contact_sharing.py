"""ContactSharing model for post-acceptance mutual contact sharing."""
import enum
from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class ContactSharingStatus(str, enum.Enum):
    PENDING = "PENDING"
    MUTUAL_CONSENT = "MUTUAL_CONSENT"
    REVOKED = "REVOKED"


class ContactSharing(Base):
    __tablename__ = "contact_sharing"

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey("bid.id"), nullable=True, unique=True, index=True)
    stock_bid_id = Column(Integer, ForeignKey("stock_bid.id"), nullable=True, unique=True, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    buyer_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    farmer_consented = Column(Boolean, nullable=False, default=False)
    farmer_consented_at = Column(DateTime, nullable=True)

    buyer_consented = Column(Boolean, nullable=False, default=False)
    buyer_consented_at = Column(DateTime, nullable=True)

    status = Column(Enum(ContactSharingStatus), nullable=False, default=ContactSharingStatus.PENDING, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    bid = relationship("Bid")
    stock_bid = relationship("StockBid")
    farmer = relationship("User", foreign_keys=[farmer_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
