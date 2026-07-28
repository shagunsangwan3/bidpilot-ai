from pydantic import BaseModel, EmailStr


class SendEmailRequest(BaseModel):
    lead_id: int

    to: EmailStr

    subject: str

    body: str

class ReplyEmailRequest(BaseModel):
    lead_id: int
    subject: str
    body: str