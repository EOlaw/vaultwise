from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..accounts.models import Account
from ..accounts.service import account_with_access, accessible_account_ids
from ..ledger.models import LedgerDirection, LedgerEntry
from ..notifications.service import notify_statement_generated
from ..transactions.models import Transaction, TransactionType
from ..users.models import User
from .models import AccountStatement, AccountStatementLine, StatementStatus
from .schemas import StatementGenerateRequest


def _signed_transaction_amount(transaction: Transaction) -> Decimal:
    if transaction.type in {TransactionType.income, TransactionType.transfer_in}:
        return Decimal(transaction.amount)
    return -Decimal(transaction.amount)


def _opening_balance(db: Session, account: Account, period_start: date) -> Decimal:
    prior_transactions = db.scalars(
        select(Transaction).where(
            Transaction.account_id == account.id,
            Transaction.occurred_on < period_start,
        )
    ).all()
    return Decimal(account.opening_balance or 0) + sum((_signed_transaction_amount(row) for row in prior_transactions), Decimal("0"))


def list_statements(db: Session, user: User, account_id: int | None = None) -> list[AccountStatement]:
    if account_id is not None:
        account_with_access(db, user.id, account_id)
        account_ids = [account_id]
    else:
        account_ids = accessible_account_ids(db, user.id)
    if not account_ids:
        return []
    return db.scalars(
        select(AccountStatement)
        .where(AccountStatement.account_id.in_(account_ids))
        .order_by(AccountStatement.period_end.desc(), AccountStatement.id.desc())
    ).unique().all()


def get_statement(db: Session, user: User, statement_id: int) -> AccountStatement:
    statement = db.get(AccountStatement, statement_id)
    if not statement:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statement not found")
    account_with_access(db, user.id, statement.account_id)
    return statement


def generate_statement(db: Session, user: User, payload: StatementGenerateRequest) -> AccountStatement:
    if payload.period_end < payload.period_start:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="period_end must be on or after period_start")
    account = account_with_access(db, user.id, payload.account_id)
    existing = db.scalar(
        select(AccountStatement).where(
            AccountStatement.account_id == account.id,
            AccountStatement.period_start == payload.period_start,
            AccountStatement.period_end == payload.period_end,
        )
    )
    if existing:
        return existing

    opening = _opening_balance(db, account, payload.period_start)
    transactions = db.scalars(
        select(Transaction).where(
            Transaction.account_id == account.id,
            Transaction.occurred_on >= payload.period_start,
            Transaction.occurred_on <= payload.period_end,
        ).order_by(Transaction.occurred_on, Transaction.id)
    ).all()
    statement = AccountStatement(
        account_id=account.id,
        user_id=account.user_id,
        organization_id=account.organization_id,
        period_start=payload.period_start,
        period_end=payload.period_end,
        opening_balance=opening,
        closing_balance=opening,
        total_debits=Decimal("0"),
        total_credits=Decimal("0"),
        status=StatementStatus.generated,
        generated_by_user_id=user.id,
    )
    db.add(statement)
    db.flush()
    running = opening
    for transaction in transactions:
        signed = _signed_transaction_amount(transaction)
        debit = abs(signed) if signed < 0 else Decimal("0")
        credit = signed if signed > 0 else Decimal("0")
        running += signed
        ledger_entry = db.scalar(select(LedgerEntry).where(LedgerEntry.transaction_id == transaction.id))
        if not ledger_entry:
            direction = LedgerDirection.credit if credit else LedgerDirection.debit
            ledger_entry = db.scalar(
                select(LedgerEntry).where(
                    LedgerEntry.account_id == account.id,
                    LedgerEntry.transfer_id.is_not(None),
                    LedgerEntry.amount == transaction.amount,
                    LedgerEntry.direction == direction,
                    LedgerEntry.effective_on == transaction.occurred_on,
                )
            )
        db.add(
            AccountStatementLine(
                statement_id=statement.id,
                transaction_id=transaction.id,
                ledger_entry_id=ledger_entry.id if ledger_entry else None,
                occurred_on=transaction.occurred_on,
                description=transaction.notes or transaction.category,
                debit=debit,
                credit=credit,
                running_balance=running,
            )
        )
        statement.total_debits += debit
        statement.total_credits += credit
    statement.closing_balance = running
    db.flush()
    notify_statement_generated(db, user_id=user.id, account_id=account.id, statement_id=statement.id, organization_id=account.organization_id)
    db.commit()
    db.refresh(statement)
    return statement
