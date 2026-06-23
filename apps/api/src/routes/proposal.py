from fastapi import APIRouter

from src.schemas.proposal import ProposalRequest
from src.agents.proposal_agent import generate_proposal

router = APIRouter(
    prefix="/proposal",
    tags=["Proposal Generator"]
)

@router.post("/")
async def create_proposal(
    payload: ProposalRequest
):
    proposal = await generate_proposal(
        payload.job_title,
        payload.job_description,
        payload.budget
    )

    return {
        "proposal": proposal
    }