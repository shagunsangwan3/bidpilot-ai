from datetime import datetime

from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int
    lead_id: int

    filename: str
    filepath: str

    created_at: datetime

    class Config:
        from_attributes = True