from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileRequest(BaseModel):
    name: str
    username: Optional[str] = None

    mobile_number: Optional[str] = None
    alt_mobile_number: Optional[str] = None
    country_code: Optional[str] = None

    date_of_birth: Optional[date] = None
    gender: Optional[str] = None

    company: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None

    website: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None

    bio: Optional[str] = None
    description: Optional[str] = None

    timezone: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    zip_code: Optional[str] = None