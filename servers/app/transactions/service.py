from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..accounts.service import account_with_access
from .models import Transaction
from .schemas import TransactionCreate, TransactionUpdate


def owned_transaction(db: Session, user_id: int, transaction_id: int) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    account_with_access(db, user_id, transaction.account_id)
    return transaction


def create_transaction(db: Session, user_id: int, payload: TransactionCreate) -> Transaction:
    account_with_access(db, user_id, payload.account_id, require_transact=True)
    transaction = Transaction(user_id=user_id, **payload.model_dump())
    db.add(transaction)
    db.flush()
    from ..ledger.service import record_transaction_ledger_entry

    record_transaction_ledger_entry(db, transaction, actor_user_id=user_id)
    db.commit()
    db.refresh(transaction)
    return transaction


def update_transaction(db: Session, transaction: Transaction, payload: TransactionUpdate) -> Transaction:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(transaction, key, value)
    db.commit()
    db.refresh(transaction)
    return transaction
