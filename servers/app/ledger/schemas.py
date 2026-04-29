from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from .models import HoldStatus, LedgerDirection, LedgerEventType


class LedgerEntryRead(BaseModel):
    id: int
    account_id: int
    organization_id: int | None
    transfer_id: int | None
    transaction_id: int | None
    direction: LedgerDirection
    event_type: LedgerEventType
    amount: Decimal
    currency: str
    description: str
    effective_on: date
    created_by_user_id: int | None
    idempotency_key: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountHoldRead(BaseModel):
    id: int
    account_id: int
    transfer_id: int | None
    card_authorization_id: int | None
    amount: Decimal
    currency: str
    reason: str
    status: HoldStatus
    created_by_user_id: int | None
    created_at: datetime
    expires_at: datetime | None
    released_at: datetime | None

    model_config = {"from_attributes": True}


class AccountBalanceRead(BaseModel):
    account_id: int
    current_balance: Decimal
    available_balance: Decimal
    held_amount: Decimal


class AccountBalanceSnapshotRead(BaseModel):
    id: int
    account_id: int
    as_of_date: date
    current_balance: Decimal
    available_balance: Decimal
    held_amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountReconciliationRead(BaseModel):
    account_id: int
    transaction_balance: Decimal
    ledger_balance: Decimal
    variance: Decimal
    active_hold_amount: Decimal
    available_balance: Decimal
    expired_active_holds: int
    terminal_transfer_active_holds: int
    status: str
    issues: list[str]


class ReconciliationSummaryRead(BaseModel):
    status: str
    account_count: int
    issue_count: int
    accounts: list[AccountReconciliationRead]
