from pydantic import BaseModel, EmailStr
from typing import Optional


class EmailCreate(BaseModel):
    lead_id: int
    sender: EmailStr
    receiver: EmailStr
    subject: str
    body: str
    direction: str = "outgoing"
    status: str = "sent"
    thread_id: Optional[str] = None
    message_id: Optional[str] = None