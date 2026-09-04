"""Rating model for 2-sided 5-star ratings between farmers and buyers."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database.base import Base


class Rating(Base):
    __tablename__ = "rating"
    __table_args__ = (
        UniqueConstraint("rater_id", "trade_order_id", name="uq_rater_tradeorder"),
    )

    id = Column(Integer, primary_key=True, index=True)
    rater_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    target_user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    trade_order_id = Column(Integer, ForeignKey("trade_order.id"), nullable=False, index=True)

    stars = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    rater = relationship("User", foreign_keys=[rater_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    trade_order = relationship("TradeOrder")

