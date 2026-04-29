import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class OrganizationType(str, enum.Enum):
    business = "business"
    nonprofit = "nonprofit"
    internal = "internal"


class OrganizationStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"
    closed = "closed"


class MembershipRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    operator = "operator"
    approver = "approver"
    viewer = "viewer"


class MembershipStatus(str, enum.Enum):
    active = "active"
    invited = "invited"
    suspended = "suspended"
    removed = "removed"


class EntitlementStatus(str, enum.Enum):
    active = "active"
    revoked = "revoked"


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    legal_name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_type: Mapped[OrganizationType] = mapped_column(Enum(OrganizationType), default=OrganizationType.business, nullable=False)
    status: Mapped[OrganizationStatus] = mapped_column(Enum(OrganizationStatus), default=OrganizationStatus.active, index=True, nullable=False)
    tax_id_last4: Mapped[str | None] = mapped_column(String(4))
    industry: Mapped[str | None] = mapped_column(String(120))
    phone: Mapped[str | None] = mapped_column(String(40))
    address_line1: Mapped[str | None] = mapped_column(String(180))
    address_line2: Mapped[str | None] = mapped_column(String(180))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(80))
    postal_code: Mapped[str | None] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(80), default="United States")
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    accounts = relationship("Account", back_populates="organization")
    memberships = relationship("OrganizationMembership", back_populates="organization", cascade="all, delete-orphan")
    entitlements = relationship("AccountEntitlement", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_membership_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    role: Mapped[MembershipRole] = mapped_column(Enum(MembershipRole), default=MembershipRole.viewer, nullable=False)
    status: Mapped[MembershipStatus] = mapped_column(Enum(MembershipStatus), default=MembershipStatus.active, index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(120))
    can_invite_members: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User")


class AccountEntitlement(Base):
    __tablename__ = "account_entitlements"
    __table_args__ = (UniqueConstraint("organization_id", "account_id", "user_id", name="uq_org_account_user_entitlement"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), index=True, nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    can_view: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_transact: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    can_approve: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    daily_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    monthly_limit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    status: Mapped[EntitlementStatus] = mapped_column(Enum(EntitlementStatus), default=EntitlementStatus.active, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)

    organization = relationship("Organization", back_populates="entitlements")
    account = relationship("Account", back_populates="entitlements")
    user = relationship("User")
