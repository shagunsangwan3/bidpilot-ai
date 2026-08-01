from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.core.auth import require_min_role
from src.models.subscription import Subscription
from src.models.payment import Payment

router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)


@router.get("/overview")
def billing_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_min_role("admin")),
):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not subscription:
        return {
            "plan": "Free",
            "status": "Inactive",
            "billing_cycle": "Monthly",
            "renewal_date": None,
            "payment_method": "Not Added",
            "usage": {
                "proposals": 0,
                "proposal_limit": 3,
                "ai_credits": 0,
                "ai_credit_limit": 10,
            },
        }

    return {
        "plan": subscription.plan,
        "status": subscription.status,
        "billing_cycle": "Monthly",
        "renewal_date": subscription.renewal_date,
        "payment_method": "Not Added",
        "usage": {
            "proposals": subscription.proposal_used,
            "proposal_limit": subscription.proposal_limit,
            "ai_credits": subscription.ai_credit_used,
            "ai_credit_limit": subscription.ai_credit_limit,
        },
    }

@router.get("/history")
def billing_history(
    db: Session = Depends(get_db),
    current_user=Depends(require_min_role("admin")),
):
    # NOTE: nothing in this codebase currently inserts Payment rows (no Razorpay
    # webhook handler exists yet to record completed payments) — this will keep
    # returning an empty list until that's built. Wiring it to the real table now
    # so it starts working the moment payments are recorded, instead of a
    # hardcoded [] that would silently mask that gap forever.
    payments = (
        db.query(Payment)
        .filter(Payment.organization_id == current_user["organization_id"])
        .order_by(Payment.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(p.id),
            "date": p.created_at.isoformat() if p.created_at else None,
            "amount": p.amount,
            "currency": p.currency,
            "status": p.status,
        }
        for p in payments
    ]

@router.get("/payment-method")
def payment_method(
    current_user=Depends(require_min_role("admin")),
    db: Session = Depends(get_db),
):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.organization_id == current_user["organization_id"]
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Subscription not found",
        )

    return {
        "type": "none",
    }