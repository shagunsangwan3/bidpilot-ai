from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src.models.proposal import Proposal
from src.schemas.proposal_save import ProposalCreate
from src.schemas.proposal import ProposalRequest
from src.agents.proposal_agent import generate_proposal
from fastapi.responses import StreamingResponse
from src.utils.pdf_generator import create_proposal_pdf
from src.models.lead import Lead
from src.utils.activity_logger import log_activity
from src.services.subscription_service import check_proposal_limit

router = APIRouter(
    prefix="/proposal",
    tags=["Proposal Generator"]
)

from src.core.auth import get_current_user

# CRITICAL: every route in this file previously had no current_user dependency
# at all — GET/PUT/DELETE required no authentication whatsoever, meaning
# anyone (logged in or not) could list every proposal from every user in the
# database, or edit/delete any proposal by guessing its ID. Every route below
# now requires auth and scopes to the caller's organization.

@router.post("/")
async def create_proposal(
    payload: ProposalRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    subscription = check_proposal_limit(
        db=db,
        organization_id=current_user["organization_id"],
    )

    proposal = await generate_proposal(
        payload.job_title,
        payload.job_description,
        payload.budget
    )

    subscription.proposal_used += 1
    subscription.ai_credit_used += 1

    db.commit()

    return {
        "proposal": proposal
    }

@router.post("/save")
def save_proposal(
    payload: ProposalCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == payload.lead_id,
            Lead.organization_id == current_user["organization_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    proposal = Proposal(
        lead_id=payload.lead_id,
        title=payload.title,
        content=payload.content,
        organization_id=current_user["organization_id"],
        created_by=current_user["user_id"],
    )

    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    log_activity(
        db=db,
        lead_id=proposal.lead_id,
        action="Proposal Saved",
        description=f"Proposal '{proposal.title}' was saved.",
    )

    return {
        "id": proposal.id,
        "message": "Proposal saved successfully",
    }

@router.get("/")
def get_proposals(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proposals = (
        db.query(Proposal, Lead)
        .join(Lead, Proposal.lead_id == Lead.id)
        .filter(Proposal.organization_id == current_user["organization_id"])
        .order_by(Proposal.created_at.desc())
        .all()
    )
    return [
        {
            "id": proposal.id,
            "lead_id": proposal.lead_id,
            "title": proposal.title,
            "content": proposal.content,
            "created_at": proposal.created_at,

            "client_name": lead.client_name,
            "client_email": lead.client_email,

            "lead_title": lead.title,
            "budget": lead.budget,
            "currency": lead.currency,
            "status": lead.status,
        }
        for proposal, lead in proposals
    ]

@router.put("/{proposal_id}")
def update_proposal(
    proposal_id: int,
    payload: ProposalCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proposal = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id,
            Proposal.organization_id == current_user["organization_id"],
        )
        .first()
    )

    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found",
        )

    proposal.title = payload.title
    proposal.content = payload.content
    proposal.lead_id = payload.lead_id

    db.commit()
    db.refresh(proposal)

    return proposal

@router.delete("/{proposal_id}")
def delete_proposal(
    proposal_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    proposal = (
        db.query(Proposal)
        .filter(
            Proposal.id == proposal_id,
            Proposal.organization_id == current_user["organization_id"],
        )
        .first()
    )

    if not proposal:
        raise HTTPException(
            status_code=404,
            detail="Proposal not found",
        )

    log_activity(
        db=db,
        lead_id=proposal.lead_id,
        action="Proposal Deleted",
        description=f"Proposal '{proposal.title}' was deleted.",
    )

    db.delete(proposal)
    db.commit()

    return {
        "message": "Proposal deleted successfully"
    }
