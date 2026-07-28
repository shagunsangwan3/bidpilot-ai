from sqlalchemy.orm import Session

from src.models.notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification