from datetime import datetime

from pydantic import BaseModel


class ProposalCreate(BaseModel):
    lead_id: int
    title: str
    content: str


class ProposalResponse(BaseModel):
    id: int
    lead_id: int
    title: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True