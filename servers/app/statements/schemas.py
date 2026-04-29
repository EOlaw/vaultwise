from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from .models import StatementStatus


class StatementGenerateRequest(BaseModel):
    account_id: int
    period_start: date
    period_end: date


class StatementLineRead(BaseModel):
    id: int
    statement_id: int
    transaction_id: int | None
    ledger_entry_id: int | None
    occurred_on: date
    description: str
    debit: Decimal
    credit: Decimal
    running_balance: Decimal

    model_config = {"from_attributes": True}


class StatementRead(BaseModel):
    id: int
    account_id: int
    user_id: int
    organization_id: int | None
    period_start: date
    period_end: date
    opening_balance: Decimal
    closing_balance: Decimal
    total_debits: Decimal
    total_credits: Decimal
    status: StatementStatus
    generated_by_user_id: int | None
    generated_at: datetime
    lines: list[StatementLineRead] = []

    model_config = {"from_attributes": True}
