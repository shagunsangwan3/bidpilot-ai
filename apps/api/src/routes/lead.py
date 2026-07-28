from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.auth import get_current_user

from src.models.lead import Lead
from src.schemas.lead import LeadCreate, LeadUpdate

from src.utils.activity import log_activity
from src.services.notification_service import create_notification

router = APIRouter(
    prefix="/leads",
    tags=["Leads"]
)


# -----------------------------
# Create Lead
# -----------------------------
@router.post("/")
def create_lead(
    payload: LeadCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = Lead(
        **payload.model_dump(),
        user_id=current_user["user_id"],
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    log_activity(
    db=db,
    lead_id=lead.id,
    action="Lead Created",
    description=f"{lead.title} was created.",
)

    create_notification(
    db=db,
    user_id=current_user["user_id"],
    title="New Lead Created",
    message=f"{lead.client_name} was added successfully.",
    notification_type="lead",
)

    return lead


# -----------------------------
# Get All Leads
# -----------------------------
@router.get("/")
def get_leads(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Lead).filter(
        Lead.user_id == current_user["user_id"]
    )

    if search:
        query = query.filter(
            Lead.title.ilike(f"%{search}%")
        )

    if status:
        query = query.filter(
            Lead.status == status
        )

    if priority:
        query = query.filter(
            Lead.priority == priority
        )

    return (
        query.order_by(Lead.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


# -----------------------------
# Get Single Lead
# -----------------------------
@router.get("/{lead_id}")
def get_lead(
    lead_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.user_id == current_user["user_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    return lead


# -----------------------------
# Update Lead
# -----------------------------
@router.put("/{lead_id}")
def update_lead(
    lead_id: int,
    payload: LeadUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.user_id == current_user["user_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    updates = payload.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(lead, key, value)

    db.commit()
    db.refresh(lead)

    return lead


# -----------------------------
# Delete Lead
# -----------------------------
@router.delete("/{lead_id}")
def delete_lead(
    lead_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.user_id == current_user["user_id"],
        )
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    db.delete(lead)
    db.commit()

    return {
        "success": True,
        "message": "Lead deleted successfully",
    }