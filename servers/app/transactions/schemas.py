from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from .models import TransactionType


class TransactionBase(BaseModel):
    account_id: int
    type: TransactionType
    amount: Decimal = Field(gt=0)
    occurred_on: date
    category: str = Field(min_length=2, max_length=80)
    tags: str | None = None
    notes: str | None = None
    receipt_url: str | None = None
    recurring_rule: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    occurred_on: date | None = None
    category: str | None = Field(default=None, min_length=2, max_length=80)
    tags: str | None = None
    notes: str | None = None
    receipt_url: str | None = None
    recurring_rule: str | None = None


class TransactionRead(TransactionBase):
    id: int

    model_config = {"from_attributes": True}
