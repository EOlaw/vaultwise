from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .models import Account
from .schemas import AccountCreate, AccountRead, AccountUpdate
from .service import account_balance, account_with_access, create_account, list_accessible_accounts, update_account


router = APIRouter(prefix="/accounts", tags=["accounts"])


def serialize_account(db: Session, account: Account) -> dict:
    return {**account.__dict__, "current_balance": account_balance(db, account)}


@router.get("", response_model=list[AccountRead])
def list_accounts(db: Session = Depends(get_db), user: User = Depends(require_permission("accounts:read"))):
    accounts = list_accessible_accounts(db, user.id)
    return [serialize_account(db, account) for account in accounts]


@router.post("", response_model=AccountRead, status_code=201)
def create(payload: AccountCreate, db: Session = Depends(get_db), user: User = Depends(require_permission("accounts:create"))):
    return serialize_account(db, create_account(db, user.id, payload))


@router.patch("/{account_id}", response_model=AccountRead)
def patch(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db), user: User = Depends(require_permission("accounts:update"))):
    account = update_account(db, account_with_access(db, user.id, account_id, require_approve=True), payload)
    return serialize_account(db, account)


@router.delete("/{account_id}", status_code=204)
def delete(account_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("accounts:delete"))):
    account = account_with_access(db, user.id, account_id, require_approve=True)
    db.delete(account)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
