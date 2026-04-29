import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class NotificationType(str, enum.Enum):
    transfer = "transfer"
    approval = "approval"
    risk = "risk"
    statement = "statement"
    system = "system"


class NotificationPriority(str, enum.Enum):
    info = "info"
    action_required = "action_required"
    warning = "warning"
    critical = "critical"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType), index=True, nullable=False)
    priority: Mapped[NotificationPriority] = mapped_column(Enum(NotificationPriority), default=NotificationPriority.info, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    action_url: Mapped[str | None] = mapped_column(String(255))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    read_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
