from sqlalchemy.orm import Session

from src.models.activity import Activity


def log_activity(
    db: Session,
    lead_id: int,
    action: str,
    description: str = "",
):
    activity = Activity(
        lead_id=lead_id,
        action=action,
        description=description,
    )

    db.add(activity)
    db.commit()

    return activity