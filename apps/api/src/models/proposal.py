from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from src.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, ForeignKey("leads.id"))

    # Proposal had NO ownership field at all before this — every route that
    # touched it was also missing an auth dependency, so this didn't matter
    # in practice, but both are fixed together now.
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    title = Column(String, nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())