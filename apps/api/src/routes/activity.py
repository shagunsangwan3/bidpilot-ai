from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.core.dependencies import get_db
from src.core.auth import get_current_user

from src.models.activity import Activity
from src.models.lead import Lead

router = APIRouter(
    prefix="/activities",
    tags=["Activities"],
)


@router.get("/{lead_id}")
def get_activities(
    lead_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(
            Lead.id == lead_id,
            Lead.organization_id == current_user["organization_id"],
        )
        .first()
    )

    if not lead:
        return []

    return (
        db.query(Activity)
        .filter(Activity.lead_id == lead_id)
        .order_by(Activity.created_at.desc())
        .all()
    )