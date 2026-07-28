from pydantic import BaseModel

class ProposalTemplateCreate(BaseModel):
    name: str
    category: str
    description: str
    content: str