import enum
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    transfer_in = "transfer_in"
    transfer_out = "transfer_out"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    occurred_on: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    tags: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    receipt_url: Mapped[str | None] = mapped_column(String(500))
    recurring_rule: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
