import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class BeneficiaryType(str, enum.Enum):
    internal_account = "internal_account"
    external_ach = "external_ach"
    wire = "wire"
    bill_pay = "bill_pay"


class BeneficiaryStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    blocked = "blocked"


class TransferType(str, enum.Enum):
    internal = "internal"
    external_ach = "external_ach"
    wire = "wire"
    bill_pay = "bill_pay"


class TransferStatus(str, enum.Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    scheduled = "scheduled"
    processing = "processing"
    posted = "posted"
    cancelled = "cancelled"
    rejected = "rejected"
    failed = "failed"


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    beneficiary_type: Mapped[BeneficiaryType] = mapped_column(Enum(BeneficiaryType), nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    bank_name: Mapped[str | None] = mapped_column(String(160))
    routing_number_last4: Mapped[str | None] = mapped_column(String(4))
    account_number_last4: Mapped[str | None] = mapped_column(String(4))
    internal_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), index=True)
    status: Mapped[BeneficiaryStatus] = mapped_column(Enum(BeneficiaryStatus), default=BeneficiaryStatus.active, index=True, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    transfers = relationship("Transfer", back_populates="beneficiary")


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    from_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    to_account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), index=True)
    beneficiary_id: Mapped[int | None] = mapped_column(ForeignKey("beneficiaries.id"), index=True)
    transfer_type: Mapped[TransferType] = mapped_column(Enum(TransferType), nullable=False)
    status: Mapped[TransferStatus] = mapped_column(Enum(TransferStatus), default=TransferStatus.draft, index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    memo: Mapped[str | None] = mapped_column(String(255))
    requested_on: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    scheduled_for: Mapped[date | None] = mapped_column(Date, index=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    beneficiary = relationship("Beneficiary", back_populates="transfers")
    events = relationship("TransferEvent", back_populates="transfer", cascade="all, delete-orphan", order_by="TransferEvent.created_at")


class TransferEvent(Base):
    __tablename__ = "transfer_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id"), index=True, nullable=False)
    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(40))
    to_status: Mapped[str | None] = mapped_column(String(40))
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    transfer = relationship("Transfer", back_populates="events")
