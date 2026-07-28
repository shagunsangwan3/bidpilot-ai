from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from fastapi import HTTPException
from src.schemas.email import ReplyEmailRequest
from src.services.email_service import send_email

from src.database import get_db
from src.models.email import Email
from src.models.lead import Lead

router = APIRouter(
    prefix="/inbox",
    tags=["Inbox"],
)


@router.get("/")
def get_all_emails(
    db: Session = Depends(get_db),
):
    results = (
        db.query(Email, Lead)
        .join(
            Lead,
            Email.lead_id == Lead.id,
        )
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
    db: Session = Depends(get_db),
):
    return (
        db.query(Email)
        .filter(Email.lead_id == lead_id)
        .order_by(Email.created_at.asc())
        .all()
    )

@router.post("/reply")
async def reply_to_email(
    payload: ReplyEmailRequest,
    db: Session = Depends(get_db),
):
    lead = (
        db.query(Lead)
        .filter(Lead.id == payload.lead_id)
        .first()
    )

    if not lead:
        raise HTTPException(
            status_code=404,
            detail="Lead not found",
        )

    print("Lead ID:", lead.id)
    print("Lead Name:", lead.client_name)
    print("Lead Email:", lead.client_email)

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