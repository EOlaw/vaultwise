import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class LedgerDirection(str, enum.Enum):
    debit = "debit"
    credit = "credit"


class LedgerEventType(str, enum.Enum):
    opening_balance = "opening_balance"
    transfer_posted = "transfer_posted"
    transaction_posted = "transaction_posted"
    adjustment = "adjustment"


class HoldStatus(str, enum.Enum):
    active = "active"
    released = "released"
    cancelled = "cancelled"
    expired = "expired"


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id"), index=True)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), index=True)
    direction: Mapped[LedgerDirection] = mapped_column(Enum(LedgerDirection), index=True, nullable=False)
    event_type: Mapped[LedgerEventType] = mapped_column(Enum(LedgerEventType), index=True, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    effective_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AccountHold(Base):
    __tablename__ = "account_holds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id"), unique=True, index=True)
    card_authorization_id: Mapped[int | None] = mapped_column(ForeignKey("card_authorizations.id"), unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[HoldStatus] = mapped_column(Enum(HoldStatus), default=HoldStatus.active, index=True, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    released_at: Mapped[datetime | None] = mapped_column(DateTime)


class AccountBalanceSnapshot(Base):
    __tablename__ = "account_balance_snapshots"
    __table_args__ = (UniqueConstraint("account_id", "as_of_date", name="uq_account_balance_snapshot_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    as_of_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    available_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    held_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
