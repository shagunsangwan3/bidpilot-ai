from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# -----------------------------
# Base Schema
# -----------------------------
class LeadBase(BaseModel):
    client_name: str = Field(..., min_length=2, max_length=255)
    client_email: Optional[EmailStr] = None
    company: Optional[str] = None
    website: Optional[str] = None

    title: str = Field(..., min_length=3, max_length=255)
    description: str
    platform: str
    category: Optional[str] = None

    budget: float = 0
    currency: str = "USD"
    estimated_value: float = 0

    status: str = "new"
    priority: str = "medium"
    probability: int = Field(default=50, ge=0, le=100)

    proposal_generated: bool = False
    proposal_sent: bool = False

    proposal_title: Optional[str] = None
    proposal_path: Optional[str] = None

    is_won: bool = False
    is_lost: bool = False

    revenue: float = 0

    notes: Optional[str] = None
    tags: Optional[str] = None

    deadline: Optional[datetime] = None
    contacted_at: Optional[datetime] = None
    proposal_sent_at: Optional[datetime] = None
    won_at: Optional[datetime] = None
    lost_at: Optional[datetime] = None


# -----------------------------
# Create Lead
# -----------------------------
class LeadCreate(LeadBase):
    pass


# -----------------------------
# Update Lead
# -----------------------------
class LeadUpdate(BaseModel):
    client_name: Optional[str] = None
    client_email: Optional[EmailStr] = None
    company: Optional[str] = None
    website: Optional[str] = None

    title: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[str] = None
    category: Optional[str] = None

    budget: Optional[float] = None
    currency: Optional[str] = None
    estimated_value: Optional[float] = None

    status: Optional[str] = None
    priority: Optional[str] = None
    probability: Optional[int] = None

    proposal_generated: Optional[bool] = None
    proposal_sent: Optional[bool] = None

    proposal_title: Optional[str] = None
    proposal_path: Optional[str] = None

    is_won: Optional[bool] = None
    is_lost: Optional[bool] = None

    revenue: Optional[float] = None

    notes: Optional[str] = None
    tags: Optional[str] = None

    deadline: Optional[datetime] = None
    contacted_at: Optional[datetime] = None
    proposal_sent_at: Optional[datetime] = None
    won_at: Optional[datetime] = None
    lost_at: Optional[datetime] = None


# -----------------------------
# Response Schema
# -----------------------------
class LeadResponse(LeadBase):
    id: int
    user_id: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True