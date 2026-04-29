from datetime import datetime

from pydantic import BaseModel

from .models import NotificationPriority, NotificationType


class NotificationRead(BaseModel):
    id: int
    user_id: int
    organization_id: int | None
    notification_type: NotificationType
    priority: NotificationPriority
    title: str
    body: str
    action_url: str | None
    metadata_json: str | None
    read_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
