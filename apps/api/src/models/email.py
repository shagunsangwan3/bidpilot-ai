from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from src.database import Base


class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(
        Integer,
        ForeignKey("leads.id", ondelete="CASCADE"),
        nullable=False,
    )

    thread_id = Column(String(255), nullable=True)

    message_id = Column(String(255), nullable=True)

    sender = Column(String(255), nullable=False)

    receiver = Column(String(255), nullable=False)

    subject = Column(String(500), nullable=False)

    body = Column(Text, nullable=False)

    direction = Column(
        String(20),
        default="outgoing",
    )

    status = Column(
        String(50),
        default="sent",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )