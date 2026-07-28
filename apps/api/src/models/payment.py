from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
)

from sqlalchemy.orm import relationship

from datetime import datetime

from src.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
    )

    subscription_id = Column(
        Integer,
        ForeignKey("subscriptions.id"),
    )

    amount = Column(Float)

    currency = Column(
        String,
        default="INR",
    )

    status = Column(
        String,
        default="paid",
    )

    razorpay_payment_id = Column(
        String,
        nullable=True,
    )

    invoice_url = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )