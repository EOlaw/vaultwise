import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class CardType(str, enum.Enum):
    debit = "debit"
    credit = "credit"
    savings = "savings"
    virtual = "virtual"


class CardNetwork(str, enum.Enum):
    visa = "visa"
    mastercard = "mastercard"


class CardStatus(str, enum.Enum):
    active = "active"
    frozen = "frozen"
    closed = "closed"
    pending_activation = "pending_activation"


class CardAuthorizationStatus(str, enum.Enum):
    approved = "approved"
    declined = "declined"
    captured = "captured"
    reversed = "reversed"


class CardTransactionChannel(str, enum.Enum):
    card_present = "card_present"
    online = "online"
    contactless = "contactless"
    atm = "atm"


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    card_type: Mapped[CardType] = mapped_column(Enum(CardType), nullable=False)
    network: Mapped[CardNetwork] = mapped_column(Enum(CardNetwork), default=CardNetwork.visa, nullable=False)
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.active, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    card_token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    last4: Mapped[str] = mapped_column(String(4), index=True, nullable=False)
    expiry_month: Mapped[int] = mapped_column(Integer, nullable=False)
    expiry_year: Mapped[int] = mapped_column(Integer, nullable=False)
    daily_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    monthly_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    frozen_at: Mapped[datetime | None] = mapped_column(DateTime)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    controls = relationship("CardControl", back_populates="card", uselist=False, cascade="all, delete-orphan")
    authorizations = relationship("CardAuthorization", back_populates="card", cascade="all, delete-orphan")


class CardControl(Base):
    __tablename__ = "card_controls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), unique=True, index=True, nullable=False)
    allow_online: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_card_present: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_contactless: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_international: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_atm: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    require_pin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_transaction_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    blocked_merchant_categories: Mapped[str | None] = mapped_column(String(500))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    card = relationship("Card", back_populates="controls")


class CardAuthorization(Base):
    __tablename__ = "card_authorizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), index=True, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    transaction_id: Mapped[int | None] = mapped_column(ForeignKey("transactions.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    merchant_name: Mapped[str] = mapped_column(String(160), nullable=False)
    merchant_category: Mapped[str] = mapped_column(String(80), nullable=False)
    merchant_country: Mapped[str] = mapped_column(String(2), default="US", nullable=False)
    card_not_present: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    channel: Mapped[CardTransactionChannel] = mapped_column(Enum(CardTransactionChannel), default=CardTransactionChannel.online, nullable=False)
    status: Mapped[CardAuthorizationStatus] = mapped_column(Enum(CardAuthorizationStatus), index=True, nullable=False)
    decline_reason: Mapped[str | None] = mapped_column(String(255))
    authorized_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime)
    reversed_at: Mapped[datetime | None] = mapped_column(DateTime)

    card = relationship("Card", back_populates="authorizations")
