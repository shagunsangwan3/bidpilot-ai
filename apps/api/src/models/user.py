from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    # --- Profile module ---
    # All new columns are nullable: this table already exists in deployed
    # databases (created via Base.metadata.create_all(), which never alters
    # existing tables), so every one of these is backfilled via migration
    # rather than assumed to exist with a default on old rows.
    username = Column(String(50), unique=True, nullable=True, index=True)

    mobile_number = Column(String(20), nullable=True)
    alt_mobile_number = Column(String(20), nullable=True)
    country_code = Column(String(8), nullable=True)

    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(30), nullable=True)

    company = Column(String(150), nullable=True)
    designation = Column(String(150), nullable=True)
    department = Column(String(150), nullable=True)

    website = Column(String(255), nullable=True)
    linkedin = Column(String(255), nullable=True)
    twitter = Column(String(255), nullable=True)
    github = Column(String(255), nullable=True)

    bio = Column(String(280), nullable=True)
    description = Column(Text, nullable=True)

    timezone = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    address = Column(String(255), nullable=True)
    zip_code = Column(String(20), nullable=True)

    # Stored the same way attachments are — a path on local disk, served back
    # through an authenticated endpoint rather than a public URL.
    profile_picture_path = Column(String(500), nullable=True)
    cover_image_path = Column(String(500), nullable=True)

    # --- Security ---
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    # Bumped whenever the user changes their password or asks to log out of
    # other sessions. Every issued JWT carries the token_version it was signed
    # with; get_current_user() rejects tokens whose version doesn't match the
    # user's current one. This is the actual revocation mechanism — JWTs are
    # stateless and can't otherwise be individually invalidated before they
    # expire.
    token_version = Column(Integer, nullable=False, default=1, server_default="1")

    # --- Organization / team membership ---
    # Each user belongs to exactly one organization (a "team of one" for solo
    # users, auto-created at registration). role is their permission level
    # within it — see models/organization.py's ROLE_RANK.
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    role = Column(String(20), nullable=False, default="owner", server_default="owner")

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
