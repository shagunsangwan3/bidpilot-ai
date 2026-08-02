from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.auth import get_current_user
from src.core.dependencies import get_db

from src.models.lead import Lead
from src.models.activity import Activity
from src.schemas.ai_assistant import WriteEmailRequest, ImproveTextRequest
from src.services.subscription_service import check_ai_credit_limit
from src.agents.ai_assistant_agent import (
    summarize_lead,
    write_email,
    improve_text,
    suggest_pricing,
)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


def _get_org_lead(lead_id: int, current_user: dict, db: Session) -> Lead:
    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id, Lead.organization_id == current_user["organization_id"])
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


def _spend_credit(db: Session, organization_id: int):
    subscription = check_ai_credit_limit(db, organization_id)
    subscription.ai_credit_used += 1
    db.commit()


@router.post("/leads/{lead_id}/summarize")
async def ai_summarize_lead(
    lead_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = _get_org_lead(lead_id, current_user, db)
    check_ai_credit_limit(db, current_user["organization_id"])

    activities = (
        db.query(Activity)
        .filter(Activity.lead_id == lead.id)
        .order_by(Activity.created_at.desc())
        .limit(5)
        .all()
    )
    activity_log = "; ".join(f"{a.action}: {a.description}" for a in activities)

    summary = await summarize_lead(
        title=lead.title,
        description=lead.description,
        notes=lead.notes,
        status=lead.status,
        activity_log=activity_log,
    )

    _spend_credit(db, current_user["organization_id"])

    return {"summary": summary}


@router.post("/leads/{lead_id}/suggest-pricing")
async def ai_suggest_pricing(
    lead_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = _get_org_lead(lead_id, current_user, db)
    check_ai_credit_limit(db, current_user["organization_id"])

    suggestion = await suggest_pricing(
        title=lead.title,
        description=lead.description,
        category=lead.category,
    )

    _spend_credit(db, current_user["organization_id"])

    return {"suggestion": suggestion}


@router.post("/write-email")
async def ai_write_email(
    payload: WriteEmailRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lead = _get_org_lead(payload.lead_id, current_user, db)
    check_ai_credit_limit(db, current_user["organization_id"])

    draft = await write_email(
        client_name=lead.client_name,
        project_title=lead.title,
        purpose=payload.purpose,
        context=payload.context,
    )

    _spend_credit(db, current_user["organization_id"])

    return {"draft": draft}


@router.post("/improve-text")
async def ai_improve_text(
    payload: ImproveTextRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_ai_credit_limit(db, current_user["organization_id"])

    result = await improve_text(payload.text, payload.instruction)

    _spend_credit(db, current_user["organization_id"])

    return {"result": result}
