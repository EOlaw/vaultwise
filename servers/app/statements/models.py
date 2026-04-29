import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class StatementStatus(str, enum.Enum):
    generated = "generated"
    voided = "voided"


class AccountStatement(Base):
    __tablename__ = "account_statements"
    __table_args__ = (UniqueConstraint("account_id", "period_start", "period_end", name="uq_statement_account_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    period_start: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    closing_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    total_debits: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    total_credits: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    status: Mapped[StatementStatus] = mapped_column(Enum(StatementStatus), default=StatementStatus.generated, index=True, nullable=False)
    generated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    lines = relationship("AccountStatementLine", back_populates="statement", cascade="all, delete-orphan", order_by="AccountStatementLine.occurred_on")


class AccountStatementLine(Base):
    __tablename__ = "account_statement_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    statement_id: Mapped[int] = mapped_column(ForeignKey("account_statements.id"), index=True, nullable=False)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), index=True)
    ledger_entry_id: Mapped[int | None] = mapped_column(ForeignKey("ledger_entries.id"), index=True)
    occurred_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    debit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    running_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)

    statement = relationship("AccountStatement", back_populates="lines")
