from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from .models import CustomerType, KycStatus, RiskRating, UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    role: UserRole = UserRole.user


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    role: UserRole | None = None
    is_active: bool | None = None


class UserProfileRead(BaseModel):
    id: int
    customer_reference: str
    customer_type: CustomerType
    kyc_status: KycStatus
    risk_rating: RiskRating
    phone: str | None
    date_of_birth: date | None
    occupation: str | None
    employer_name: str | None
    business_name: str | None
    annual_income: Decimal | None
    address_line1: str | None
    address_line2: str | None
    city: str | None
    state: str | None
    postal_code: str | None
    country: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRead(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    profile: UserProfileRead | None = None

    model_config = {"from_attributes": True}
