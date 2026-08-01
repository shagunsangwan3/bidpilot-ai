from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from src.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    logo_path = Column(String(500), nullable=True)

    address = Column(String(255), nullable=True)
    gst_number = Column(String(50), nullable=True)
    website = Column(String(255), nullable=True)
    industry = Column(String(150), nullable=True)
    employee_count = Column(String(30), nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


ROLE_RANK = {
    "viewer": 0,
    "sales": 1,
    "manager": 2,
    "admin": 3,
    "owner": 4,
}

VALID_ROLES = list(ROLE_RANK.keys())


class OrganizationInvite(Base):
    """A pending invite for someone who may or may not have an account yet.
    Consumed (deleted) once accepted — active membership then lives directly
    on User.organization_id / User.role, not in this table.
    """

    __tablename__ = "organization_invites"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    email = Column(String(255), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="sales")

    invited_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
