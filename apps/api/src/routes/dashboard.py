from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.core.auth import get_current_user
from src.core.dependencies import get_db
from src.models.lead import Lead

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user["user_id"]

    leads = (
        db.query(Lead)
        .filter(Lead.user_id == user_id)
        .all()
    )

    total_leads = len(leads)

    active = len([
        l for l in leads
        if l.status not in ["won", "lost"]
    ])

    won = len([
        l for l in leads
        if l.status == "won"
    ])

    lost = len([
        l for l in leads
        if l.status == "lost"
    ])

    proposal = len([
        l for l in leads
        if l.status == "proposal"
    ])

    pipeline_value = sum(
        float(l.budget or 0)
        for l in leads
    )

    won_revenue = sum(
        float(l.revenue or 0)
        for l in leads
        if l.status == "won"
    )

    conversion_rate = (
        round((won / total_leads) * 100, 2)
        if total_leads
        else 0
    )

    recent_leads = [
        {
            "id": l.id,
            "title": l.title,
            "status": l.status,
            "budget": l.budget,
            "platform": l.platform,
        }
        for l in sorted(
            leads,
            key=lambda x: x.id,
            reverse=True
        )[:5]
    ]

    return {
        "total_leads": total_leads,
        "active": active,
        "won": won,
        "lost": lost,
        "proposal": proposal,
        "pipeline_value": pipeline_value,
        "won_revenue": won_revenue,
        "conversion_rate": conversion_rate,
        "recent_leads": recent_leads,
    }