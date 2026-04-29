from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..accounts.models import Account
from ..accounts.service import account_balance, account_with_access, accessible_account_ids
from ..transactions.models import Transaction
from ..transfers.models import Transfer, TransferStatus, TransferType
from ..users.models import User
from .models import AccountBalanceSnapshot, AccountHold, HoldStatus, LedgerDirection, LedgerEntry, LedgerEventType


def active_hold_amount(db: Session, account_id: int) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(AccountHold.amount), 0)).where(
            AccountHold.account_id == account_id,
            AccountHold.status == HoldStatus.active,
        )
    )
    return Decimal(total or 0)


def available_balance(db: Session, account: Account) -> Decimal:
    return account_balance(db, account) - active_hold_amount(db, account.id)


def account_balance_payload(db: Session, account: Account) -> dict:
    held = active_hold_amount(db, account.id)
    current = account_balance(db, account)
    return {
        "account_id": account.id,
        "current_balance": current,
        "available_balance": current - held,
        "held_amount": held,
    }


def assert_available_funds(db: Session, account: Account, amount: Decimal, *, transfer: Transfer | None = None) -> None:
    held_for_transfer = Decimal("0")
    if transfer:
        existing_hold = db.scalar(
            select(AccountHold).where(
                AccountHold.transfer_id == transfer.id,
                AccountHold.account_id == account.id,
                AccountHold.status == HoldStatus.active,
            )
        )
        if existing_hold:
            held_for_transfer = Decimal(existing_hold.amount)
    if available_balance(db, account) + held_for_transfer < amount:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient available balance")


def create_hold_for_transfer(db: Session, transfer: Transfer, *, actor_user_id: int | None, reason: str) -> AccountHold:
    existing = db.scalar(select(AccountHold).where(AccountHold.transfer_id == transfer.id))
    if existing:
        if existing.status != HoldStatus.active:
            existing.status = HoldStatus.active
            existing.released_at = None
        existing.amount = transfer.amount
        existing.reason = reason
        return existing
    account = db.get(Account, transfer.from_account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    assert_available_funds(db, account, Decimal(transfer.amount), transfer=transfer)
    hold = AccountHold(
        account_id=transfer.from_account_id,
        transfer_id=transfer.id,
        amount=transfer.amount,
        currency=transfer.currency,
        reason=reason,
        status=HoldStatus.active,
        created_by_user_id=actor_user_id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(hold)
    return hold


def release_hold_for_transfer(db: Session, transfer_id: int, *, status_value: HoldStatus = HoldStatus.released) -> AccountHold | None:
    hold = db.scalar(select(AccountHold).where(AccountHold.transfer_id == transfer_id, AccountHold.status == HoldStatus.active))
    if not hold:
        return None
    hold.status = status_value
    hold.released_at = datetime.utcnow()
    return hold


def create_hold_for_card_authorization(
    db: Session,
    *,
    account_id: int,
    card_authorization_id: int,
    amount: Decimal,
    currency: str,
    actor_user_id: int | None,
    reason: str,
) -> AccountHold:
    existing = db.scalar(select(AccountHold).where(AccountHold.card_authorization_id == card_authorization_id))
    if existing:
        if existing.status != HoldStatus.active:
            existing.status = HoldStatus.active
            existing.released_at = None
        existing.amount = amount
        existing.reason = reason
        return existing
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    assert_available_funds(db, account, amount)
    hold = AccountHold(
        account_id=account_id,
        card_authorization_id=card_authorization_id,
        amount=amount,
        currency=currency,
        reason=reason,
        status=HoldStatus.active,
        created_by_user_id=actor_user_id,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(hold)
    return hold


def release_hold_for_card_authorization(db: Session, card_authorization_id: int, *, status_value: HoldStatus = HoldStatus.released) -> AccountHold | None:
    hold = db.scalar(
        select(AccountHold).where(
            AccountHold.card_authorization_id == card_authorization_id,
            AccountHold.status == HoldStatus.active,
        )
    )
    if not hold:
        return None
    hold.status = status_value
    hold.released_at = datetime.utcnow()
    return hold


def _add_ledger_entry(
    db: Session,
    *,
    account_id: int,
    organization_id: int | None,
    transfer_id: int | None,
    transaction_id: int | None,
    direction: LedgerDirection,
    event_type: LedgerEventType,
    amount: Decimal,
    currency: str,
    description: str,
    effective_on: date,
    created_by_user_id: int | None,
    idempotency_key: str,
) -> LedgerEntry:
    existing = db.scalar(select(LedgerEntry).where(LedgerEntry.idempotency_key == idempotency_key))
    if existing:
        return existing
    entry = LedgerEntry(
        account_id=account_id,
        organization_id=organization_id,
        transfer_id=transfer_id,
        transaction_id=transaction_id,
        direction=direction,
        event_type=event_type,
        amount=amount,
        currency=currency,
        description=description,
        effective_on=effective_on,
        created_by_user_id=created_by_user_id,
        idempotency_key=idempotency_key,
    )
    db.add(entry)
    return entry


def record_transfer_ledger_entries(db: Session, transfer: Transfer, *, actor_user_id: int | None) -> list[LedgerEntry]:
    entries: list[LedgerEntry] = []
    source_account = db.get(Account, transfer.from_account_id)
    if not source_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    entries.append(
        _add_ledger_entry(
            db,
            account_id=transfer.from_account_id,
            organization_id=transfer.organization_id,
            transfer_id=transfer.id,
            transaction_id=None,
            direction=LedgerDirection.debit,
            event_type=LedgerEventType.transfer_posted,
            amount=transfer.amount,
            currency=transfer.currency,
            description=transfer.memo or f"{transfer.transfer_type.value} transfer",
            effective_on=date.today(),
            created_by_user_id=actor_user_id,
            idempotency_key=f"transfer:{transfer.id}:debit:{transfer.from_account_id}",
        )
    )
    if transfer.transfer_type == TransferType.internal and transfer.to_account_id is not None:
        to_account = db.get(Account, transfer.to_account_id)
        if not to_account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination account not found")
        entries.append(
            _add_ledger_entry(
                db,
                account_id=to_account.id,
                organization_id=to_account.organization_id,
                transfer_id=transfer.id,
                transaction_id=None,
                direction=LedgerDirection.credit,
                event_type=LedgerEventType.transfer_posted,
                amount=transfer.amount,
                currency=transfer.currency,
                description=transfer.memo or "Internal transfer",
                effective_on=date.today(),
                created_by_user_id=actor_user_id,
                idempotency_key=f"transfer:{transfer.id}:credit:{to_account.id}",
            )
        )
    release_hold_for_transfer(db, transfer.id)
    return entries


def record_transaction_ledger_entry(db: Session, transaction: Transaction, *, actor_user_id: int | None) -> LedgerEntry:
    from ..transactions.models import TransactionType

    direction = LedgerDirection.credit if transaction.type in {TransactionType.income, TransactionType.transfer_in} else LedgerDirection.debit
    account = db.get(Account, transaction.account_id)
    return _add_ledger_entry(
        db,
        account_id=transaction.account_id,
        organization_id=account.organization_id if account else None,
        transfer_id=None,
        transaction_id=transaction.id,
        direction=direction,
        event_type=LedgerEventType.transaction_posted,
        amount=transaction.amount,
        currency="USD",
        description=transaction.notes or transaction.category,
        effective_on=transaction.occurred_on,
        created_by_user_id=actor_user_id,
        idempotency_key=f"transaction:{transaction.id}:{direction.value}",
    )


def snapshot_account_balance(db: Session, account: Account, as_of_date: date | None = None) -> AccountBalanceSnapshot:
    snapshot_date = as_of_date or date.today()
    payload = account_balance_payload(db, account)
    snapshot = db.scalar(
        select(AccountBalanceSnapshot).where(
            AccountBalanceSnapshot.account_id == account.id,
            AccountBalanceSnapshot.as_of_date == snapshot_date,
        )
    )
    if snapshot:
        snapshot.current_balance = payload["current_balance"]
        snapshot.available_balance = payload["available_balance"]
        snapshot.held_amount = payload["held_amount"]
    else:
        snapshot = AccountBalanceSnapshot(as_of_date=snapshot_date, **payload)
        db.add(snapshot)
    return snapshot


def list_account_ledger_entries(db: Session, user: User, account_id: int) -> list[LedgerEntry]:
    account_with_access(db, user.id, account_id)
    return db.scalars(select(LedgerEntry).where(LedgerEntry.account_id == account_id).order_by(LedgerEntry.effective_on.desc(), LedgerEntry.id.desc())).all()


def list_account_holds(db: Session, user: User, account_id: int | None = None, status_filter: HoldStatus | None = None) -> list[AccountHold]:
    account_ids = [account_id] if account_id is not None else accessible_account_ids(db, user.id)
    if account_id is not None:
        account_with_access(db, user.id, account_id)
    if not account_ids:
        return []
    query = select(AccountHold).where(AccountHold.account_id.in_(account_ids))
    if status_filter is not None:
        query = query.where(AccountHold.status == status_filter)
    return db.scalars(query.order_by(AccountHold.created_at.desc(), AccountHold.id.desc())).all()


def expire_stale_holds(db: Session, *, now: datetime | None = None, limit: int = 500) -> dict:
    effective_now = now or datetime.utcnow()
    holds = db.scalars(
        select(AccountHold)
        .where(
            AccountHold.status == HoldStatus.active,
            AccountHold.expires_at.is_not(None),
            AccountHold.expires_at <= effective_now,
        )
        .order_by(AccountHold.expires_at, AccountHold.id)
        .limit(limit)
    ).all()
    for hold in holds:
        hold.status = HoldStatus.expired
        hold.released_at = effective_now
    db.commit()
    return {
        "expired": len(holds),
        "hold_ids": [hold.id for hold in holds],
        "processed_at": effective_now.isoformat(),
    }


def reconcile_account(db: Session, account: Account) -> dict:
    transaction_balance = account_balance(db, account)
    credit_total = Decimal(
        db.scalar(
            select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
                LedgerEntry.account_id == account.id,
                LedgerEntry.direction == LedgerDirection.credit,
            )
        )
        or 0
    )
    debit_total = Decimal(
        db.scalar(
            select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
                LedgerEntry.account_id == account.id,
                LedgerEntry.direction == LedgerDirection.debit,
            )
        )
        or 0
    )
    ledger_balance = Decimal(account.opening_balance or 0) + credit_total - debit_total
    active_holds = active_hold_amount(db, account.id)
    expired_active_holds = db.scalar(
        select(func.count(AccountHold.id)).where(
            AccountHold.account_id == account.id,
            AccountHold.status == HoldStatus.active,
            AccountHold.expires_at.is_not(None),
            AccountHold.expires_at <= datetime.utcnow(),
        )
    )
    posted_transfer_holds = db.scalar(
        select(func.count(AccountHold.id))
        .join(Transfer, Transfer.id == AccountHold.transfer_id)
        .where(
            AccountHold.account_id == account.id,
            AccountHold.status == HoldStatus.active,
            Transfer.status.in_([TransferStatus.posted, TransferStatus.cancelled, TransferStatus.failed, TransferStatus.rejected]),
        )
    )
    variance = transaction_balance - ledger_balance
    issues: list[str] = []
    if variance != Decimal("0"):
        issues.append("transaction_ledger_balance_mismatch")
    if expired_active_holds:
        issues.append("expired_active_holds")
    if posted_transfer_holds:
        issues.append("terminal_transfer_active_holds")
    return {
        "account_id": account.id,
        "transaction_balance": transaction_balance,
        "ledger_balance": ledger_balance,
        "variance": variance,
        "active_hold_amount": active_holds,
        "available_balance": transaction_balance - active_holds,
        "expired_active_holds": int(expired_active_holds or 0),
        "terminal_transfer_active_holds": int(posted_transfer_holds or 0),
        "status": "ok" if not issues else "attention_required",
        "issues": issues,
    }


def reconcile_accessible_accounts(db: Session, user: User, account_id: int | None = None) -> dict:
    if account_id is not None:
        accounts = [account_with_access(db, user.id, account_id)]
    else:
        account_ids = accessible_account_ids(db, user.id)
        accounts = db.scalars(select(Account).where(Account.id.in_(account_ids)).order_by(Account.id)).all() if account_ids else []
    rows = [reconcile_account(db, account) for account in accounts]
    return {
        "status": "ok" if all(row["status"] == "ok" for row in rows) else "attention_required",
        "account_count": len(rows),
        "issue_count": sum(len(row["issues"]) for row in rows),
        "accounts": rows,
    }
