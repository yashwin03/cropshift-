"""Report model for marketplace misconduct reporting with moderation workflow."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from ..database.base import Base


class Report(Base):
    __tablename__ = "report"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    trade_order_id = Column(Integer, ForeignKey("trade_order.id"), nullable=True, index=True)

    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="PENDING_REVIEW", nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    reporter = relationship("User", foreign_keys=[reporter_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    trade_order = relationship("TradeOrder")
