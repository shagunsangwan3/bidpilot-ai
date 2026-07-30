from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from src.database import Base


class LoginSession(Base):
    """One row per successful login. Backs both the Login History list and the
    Active Sessions / 'log out of other devices' feature. Revocation of a
    stateless JWT isn't possible on its own — see User.token_version, which is
    the actual mechanism that invalidates tokens; this table is what's shown to
    the user and what a revoke action updates the flag on for display purposes.
    """

    __tablename__ = "login_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(500), nullable=True)
    browser = Column(String(100), nullable=True)
    operating_system = Column(String(100), nullable=True)

    # NOTE: no geo-IP lookup is wired up (would need a real service like
    # ipapi.co or MaxMind, not something to fake) — location is intentionally
    # left null rather than showing a fabricated city/country.
    location = Column(String(150), nullable=True)

    revoked = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
