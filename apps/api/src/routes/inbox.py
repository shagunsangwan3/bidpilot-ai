from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import HTTPException
from src.schemas.email import ReplyEmailRequest
from src.services.email_service import send_email

from src.database import get_db
from src.models.email import Email
from src.models.lead import Lead
from src.core.auth import get_current_user

router = APIRouter(
    prefix="/inbox",
    tags=["Inbox"],
)

# CRITICAL: every route in this file previously had no auth dependency at
# all — anyone, unauthenticated, could read every inbox message across every
# user's leads, read a specific lead's private conversation by ID, and send
# an email "from" any lead to any address using this server's mail
# credentials. Every route now requires login and scopes to leads within the
# caller's organization.


@router.get("/")
def get_all_emails(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = (
        db.query(Email, Lead)
        .join(Lead, Email.lead_id == Lead.id)
        .filter(Lead.organization_id == current_user["organization_id"])
        .order_by(Email.created_at.desc())
        .all()
    )

    response = []

    for email, lead in results:
        response.append(
            {
                "id": email.id,
                "lead_id": lead.id,
                "client_name": lead.client_name,
                "company": lead.company,
                "client_email": lead.client_email,
                "subject": email.subject,
                "body": email.body,
                "status": email.status,
                "direction": email.direction,
                "created_at": email.created_at,
            }
        )

    return response


@router.get("/lead/{lead_id}")
def get_lead_conversation(
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
        raise HTTPException(status_code=404, detail="Lead not found")

    return (
        db.query(Email)
        .filter(Email.lead_id == lead_id)
        .order_by(Email.created_at.asc())
        .all()
    )

@router.post("/reply")
async def reply_to_email(
    payload: ReplyEmailRequest,
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
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    await send_email(
        to=lead.client_email,
        subject=payload.subject,
        body=payload.body,
    )

    # Save sent email
    email = Email(
        lead_id=lead.id,
        subject=payload.subject,
        body=payload.body,
        status="sent",
        direction="outgoing",
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return {
        "success": True,
        "message": "Email sent successfully",
        "email": email.id,
    }
