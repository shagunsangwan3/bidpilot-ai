from pydantic import BaseModel

class ProposalRequest(BaseModel):
    job_title: str
    job_description: str
    budget: str