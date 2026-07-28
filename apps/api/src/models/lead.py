from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from src.database import Base


class Lead(Base):
    __tablename__ = "leads"

    # -----------------------------
    # Primary Key
    # -----------------------------
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # -----------------------------
    # Owner
    # -----------------------------
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # -----------------------------
    # Client Information
    # -----------------------------
    client_name = Column(
        String(255),
        nullable=False,
    )

    client_email = Column(
        String(255),
        nullable=True,
    )

    company = Column(
        String(255),
        nullable=True,
    )

    website = Column(
        String(255),
        nullable=True,
    )

    # -----------------------------
    # Job Details
    # -----------------------------
    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    platform = Column(
        String(100),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=True,
    )

    # -----------------------------
    # Budget
    # -----------------------------
    budget = Column(
        Float,
        default=0,
    )

    currency = Column(
        String(10),
        default="USD",
    )

    estimated_value = Column(
        Float,
        default=0,
    )

    # -----------------------------
    # Lead Status
    # -----------------------------
    status = Column(
        String(50),
        default="new",
        index=True,
    )

    priority = Column(
        String(20),
        default="medium",
    )

    probability = Column(
        Integer,
        default=50,
    )

    # -----------------------------
    # Proposal
    # -----------------------------
    proposal_generated = Column(
        Boolean,
        default=False,
    )

    proposal_sent = Column(
        Boolean,
        default=False,
    )

    proposal_title = Column(
        String(255),
        nullable=True,
    )

    proposal_path = Column(
        String(500),
        nullable=True,
    )

    # -----------------------------
    # Revenue
    # -----------------------------
    is_won = Column(
        Boolean,
        default=False,
    )

    is_lost = Column(
        Boolean,
        default=False,
    )

    revenue = Column(
        Float,
        default=0,
    )

    # -----------------------------
    # Notes
    # -----------------------------
    notes = Column(
        Text,
        nullable=True,
    )

    tags = Column(
        String(500),
        nullable=True,
    )

    # -----------------------------
    # Dates
    # -----------------------------
    deadline = Column(
        DateTime,
        nullable=True,
    )

    contacted_at = Column(
        DateTime,
        nullable=True,
    )

    proposal_sent_at = Column(
        DateTime,
        nullable=True,
    )

    won_at = Column(
        DateTime,
        nullable=True,
    )

    lost_at = Column(
        DateTime,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )