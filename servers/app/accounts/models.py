import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class AccountType(str, enum.Enum):
    cash = "cash"
    bank = "bank"
    credit_card = "credit_card"
    investment = "investment"
    loan = "loan"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)
    institution: Mapped[str | None] = mapped_column(String(120))
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0)
    interest_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="accounts")
    organization = relationship("Organization", back_populates="accounts")
    entitlements = relationship("AccountEntitlement", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account")
