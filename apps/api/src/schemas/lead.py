from pydantic import BaseModel

class LeadCreate(BaseModel):
    title: str
    platform: str
    budget: str
    description: str