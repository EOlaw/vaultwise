from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .models import EntitlementStatus, MembershipRole, MembershipStatus, OrganizationStatus, OrganizationType


class OrganizationBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    legal_name: str = Field(min_length=2, max_length=200)
    organization_type: OrganizationType = OrganizationType.business
    tax_id_last4: str | None = Field(default=None, min_length=4, max_length=4)
    industry: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    address_line1: str | None = Field(default=None, max_length=180)
    address_line2: str | None = Field(default=None, max_length=180)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=80)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str = Field(default="United States", max_length=80)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    legal_name: str | None = Field(default=None, min_length=2, max_length=200)
    status: OrganizationStatus | None = None
    tax_id_last4: str | None = Field(default=None, min_length=4, max_length=4)
    industry: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    address_line1: str | None = Field(default=None, max_length=180)
    address_line2: str | None = Field(default=None, max_length=180)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=80)
    postal_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default=None, max_length=80)


class OrganizationRead(OrganizationBase):
    id: int
    status: OrganizationStatus
    created_by_user_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MembershipCreate(BaseModel):
    user_id: int
    role: MembershipRole = MembershipRole.viewer
    title: str | None = Field(default=None, max_length=120)
    can_invite_members: bool = False


class MembershipUpdate(BaseModel):
    role: MembershipRole | None = None
    status: MembershipStatus | None = None
    title: str | None = Field(default=None, max_length=120)
    can_invite_members: bool | None = None


class MembershipRead(BaseModel):
    id: int
    organization_id: int
    user_id: int
    role: MembershipRole
    status: MembershipStatus
    title: str | None
    can_invite_members: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class EntitlementCreate(BaseModel):
    account_id: int
    user_id: int
    can_view: bool = True
    can_transact: bool = False
    can_approve: bool = False
    daily_limit: Decimal | None = Field(default=None, ge=0)
    monthly_limit: Decimal | None = Field(default=None, ge=0)


class EntitlementUpdate(BaseModel):
    can_view: bool | None = None
    can_transact: bool | None = None
    can_approve: bool | None = None
    daily_limit: Decimal | None = Field(default=None, ge=0)
    monthly_limit: Decimal | None = Field(default=None, ge=0)
    status: EntitlementStatus | None = None


class EntitlementRead(BaseModel):
    id: int
    organization_id: int
    account_id: int
    user_id: int
    can_view: bool
    can_transact: bool
    can_approve: bool
    daily_limit: Decimal | None
    monthly_limit: Decimal | None
    status: EntitlementStatus
    created_at: datetime
    revoked_at: datetime | None

    model_config = {"from_attributes": True}
