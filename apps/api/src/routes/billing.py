from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.core.auth import get_current_user
from src.models.subscription import Subscription

router = APIRouter(
    prefix="/billing",
    tags=["Billing"],
)


@router.get("/overview")
def billing_overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user["user_id"]
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
def billing_history():
    return []

@router.get("/payment-method")
def payment_method(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user["user_id"]
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