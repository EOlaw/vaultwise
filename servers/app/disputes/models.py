import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class DisputeReason(str, enum.Enum):
    fraud = "fraud"
    duplicate = "duplicate"
    goods_not_received = "goods_not_received"
    incorrect_amount = "incorrect_amount"
    cancelled_service = "cancelled_service"
    other = "other"


class DisputeStatus(str, enum.Enum):
    open = "open"
    under_review = "under_review"
    provisional_credit = "provisional_credit"
    won = "won"
    lost = "lost"
    closed = "closed"


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), index=True)
    card_authorization_id: Mapped[int | None] = mapped_column(ForeignKey("card_authorizations.id"), index=True)
    reason: Mapped[DisputeReason] = mapped_column(Enum(DisputeReason), index=True, nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(Enum(DisputeStatus), default=DisputeStatus.open, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    provisional_transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), index=True)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    events = relationship("DisputeEvent", back_populates="dispute", cascade="all, delete-orphan", order_by="DisputeEvent.created_at")


class DisputeEvent(Base):
    __tablename__ = "dispute_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dispute_id: Mapped[int] = mapped_column(ForeignKey("disputes.id"), index=True, nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(40))
    to_status: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    dispute = relationship("Dispute", back_populates="events")
