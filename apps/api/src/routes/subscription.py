from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from src.core.auth import get_current_user
from src.core.dependencies import get_db

from src.models.subscription import Subscription
from src.services.razorpay_service import create_subscription

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
)


@router.post("/create")
def create_user_subscription(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan_id = os.getenv("RAZORPAY_PLAN_ID")

    if not plan_id:
        raise HTTPException(
            status_code=500,
            detail="RAZORPAY_PLAN_ID is not configured.",
        )

    razorpay_subscription = create_subscription(plan_id)

    subscription = Subscription(
        user_id=current_user["user_id"],
        razorpay_subscription_id=razorpay_subscription["id"],
        plan="Pro",
        status=razorpay_subscription["status"],
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return {
        "subscription_id": razorpay_subscription["id"],
        "status": razorpay_subscription["status"],
        "plan": "Pro",
    }