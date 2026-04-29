from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..accounts.service import account_with_access
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .models import HoldStatus
from .schemas import AccountBalanceRead, AccountBalanceSnapshotRead, AccountHoldRead, LedgerEntryRead, ReconciliationSummaryRead
from .service import account_balance_payload, list_account_holds, list_account_ledger_entries, reconcile_accessible_accounts, snapshot_account_balance


router = APIRouter(prefix="/ledger", tags=["ledger"])


@router.get("/accounts/{account_id}/balance", response_model=AccountBalanceRead)
def get_balance(account_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("ledger:read"))):
    account = account_with_access(db, user.id, account_id)
    return account_balance_payload(db, account)


@router.get("/accounts/{account_id}/entries", response_model=list[LedgerEntryRead])
def entries(account_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("ledger:read"))):
    return list_account_ledger_entries(db, user, account_id)


@router.get("/holds", response_model=list[AccountHoldRead])
def holds(
    account_id: int | None = None,
    status_filter: HoldStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("ledger:read")),
):
    return list_account_holds(db, user, account_id, status_filter)


@router.get("/reconciliation", response_model=ReconciliationSummaryRead)
def reconciliation(
    account_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("ledger:read")),
):
    return reconcile_accessible_accounts(db, user, account_id)


@router.post("/accounts/{account_id}/snapshot", response_model=AccountBalanceSnapshotRead)
def snapshot(
    account_id: int,
    as_of_date: date | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("ledger:manage")),
):
    account = account_with_access(db, user.id, account_id)
    snapshot_row = snapshot_account_balance(db, account, as_of_date)
    db.commit()
    db.refresh(snapshot_row)
    return snapshot_row
