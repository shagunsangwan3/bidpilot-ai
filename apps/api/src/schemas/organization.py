from pydantic import BaseModel, EmailStr
from typing import Optional


class UpdateOrganizationRequest(BaseModel):
    name: str
    address: Optional[str] = None
    gst_number: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str


class ChangeRoleRequest(BaseModel):
    role: str
