from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .schemas import NotificationRead
from .service import list_notifications, mark_all_read, mark_notification_read


router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationRead])
def notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("notifications:read")),
):
    return list_notifications(db, user, unread_only)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("notifications:read"))):
    return mark_notification_read(db, user, notification_id)


@router.post("/read-all")
def read_all(db: Session = Depends(get_db), user: User = Depends(require_permission("notifications:read"))):
    return {"updated": mark_all_read(db, user)}
