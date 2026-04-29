from datetime import date
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import require_permission
from ..accounts.service import accessible_account_ids
from ..users.models import User
from .models import Transaction
from .schemas import TransactionCreate, TransactionRead, TransactionUpdate
from .service import create_transaction, owned_transaction, update_transaction


router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    start: date | None = None,
    end: date | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("transactions:read")),
):
    account_ids = accessible_account_ids(db, user.id)
    if not account_ids:
        return []
    query = select(Transaction).where(Transaction.account_id.in_(account_ids))
    if start:
        query = query.where(Transaction.occurred_on >= start)
    if end:
        query = query.where(Transaction.occurred_on <= end)
    if category:
        query = query.where(Transaction.category == category)
    return db.scalars(query.order_by(Transaction.occurred_on.desc(), Transaction.id.desc())).all()


@router.post("", response_model=TransactionRead, status_code=201)
def create(payload: TransactionCreate, db: Session = Depends(get_db), user: User = Depends(require_permission("transactions:create"))):
    return create_transaction(db, user.id, payload)


@router.patch("/{transaction_id}", response_model=TransactionRead)
def patch(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db), user: User = Depends(require_permission("transactions:update"))):
    return update_transaction(db, owned_transaction(db, user.id, transaction_id), payload)


@router.delete("/{transaction_id}", status_code=204)
def delete(transaction_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("transactions:delete"))):
    transaction = owned_transaction(db, user.id, transaction_id)
    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
