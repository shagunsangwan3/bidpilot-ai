from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.auth import get_current_user

from src.schemas.lead import LeadCreate
from src.models.lead import Lead

router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)

@router.post("/")
def create_lead(
    payload: LeadCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    lead = Lead(
        title=payload.title,
        platform=payload.platform,
        budget=payload.budget,
        description=payload.description,
        user_id=current_user["user_id"]
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return lead


@router.get("/")
def get_leads(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Lead)
        .filter(
            Lead.user_id == current_user["user_id"]
        )
        .all()
    )