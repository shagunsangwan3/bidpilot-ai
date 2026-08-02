from pydantic import BaseModel
from typing import Optional


class WriteEmailRequest(BaseModel):
    lead_id: int
    purpose: str
    context: Optional[str] = None


class ImproveTextRequest(BaseModel):
    text: str
    instruction: str
