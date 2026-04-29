from decimal import Decimal
from pydantic import BaseModel, Field
from .models import AccountType


class AccountBase(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    type: AccountType
    institution: str | None = None
    opening_balance: Decimal = Decimal("0")
    interest_rate: Decimal = Decimal("0")


class AccountCreate(AccountBase):
    organization_id: int | None = None


class AccountUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    institution: str | None = None
    opening_balance: Decimal | None = None
    interest_rate: Decimal | None = None


class AccountRead(AccountBase):
    id: int
    user_id: int
    organization_id: int | None
    current_balance: Decimal

    model_config = {"from_attributes": True}
