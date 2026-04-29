import enum
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class CustomerType(str, enum.Enum):
    personal = "personal"
    business = "business"
    internal = "internal"


class KycStatus(str, enum.Enum):
    not_started = "not_started"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class RiskRating(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="owner", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True, nullable=False)
    customer_reference: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    customer_type: Mapped[CustomerType] = mapped_column(Enum(CustomerType), nullable=False)
    kyc_status: Mapped[KycStatus] = mapped_column(Enum(KycStatus), default=KycStatus.pending, nullable=False)
    risk_rating: Mapped[RiskRating] = mapped_column(Enum(RiskRating), default=RiskRating.low, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(40))
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    occupation: Mapped[str | None] = mapped_column(String(120))
    employer_name: Mapped[str | None] = mapped_column(String(160))
    business_name: Mapped[str | None] = mapped_column(String(160))
    annual_income: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    address_line1: Mapped[str | None] = mapped_column(String(180))
    address_line2: Mapped[str | None] = mapped_column(String(180))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(80))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(80), default="United States")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="profile")
