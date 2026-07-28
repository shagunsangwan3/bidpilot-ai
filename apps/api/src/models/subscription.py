from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
)
from sqlalchemy.sql import func

from src.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    plan = Column(String(30), default="Free")

    status = Column(String(30), default="active")

    razorpay_subscription_id = Column(
        String(120),
        nullable=True,
    )

    proposal_limit = Column(Integer, default=3)
    proposal_used = Column(Integer, default=0)

    ai_credit_limit = Column(Integer, default=10)
    ai_credit_used = Column(Integer, default=0)

    renewal_date = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )