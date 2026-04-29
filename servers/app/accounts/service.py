from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import Account
from .schemas import AccountCreate, AccountUpdate
from ..iam.policies import INTERNAL_ROLES
from ..iam.service import user_role_names
from ..organizations.models import (
    AccountEntitlement,
    EntitlementStatus,
    MembershipRole,
    MembershipStatus,
    Organization,
    OrganizationMembership,
    OrganizationStatus,
)
from ..transactions.models import Transaction, TransactionType


INTERNAL_ACCOUNT_MANAGERS = {"super_admin", "bank_admin"}
ORG_ACCOUNT_MANAGERS = {MembershipRole.owner, MembershipRole.admin}


def account_balance(db: Session, account: Account) -> Decimal:
    income = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.account_id == account.id,
        Transaction.type.in_([TransactionType.income, TransactionType.transfer_in]),
    ))
    outflow = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.account_id == account.id,
        Transaction.type.in_([TransactionType.expense, TransactionType.transfer_out]),
    ))
    return Decimal(account.opening_balance or 0) + Decimal(income or 0) - Decimal(outflow or 0)


def _user_roles(db: Session, user_id: int) -> set[str]:
    return user_role_names(db, user_id)


def _is_internal(db: Session, user_id: int) -> bool:
    return bool(_user_roles(db, user_id) & INTERNAL_ROLES)


def _is_internal_account_manager(db: Session, user_id: int) -> bool:
    return bool(_user_roles(db, user_id) & INTERNAL_ACCOUNT_MANAGERS)


def _active_membership(db: Session, *, organization_id: int, user_id: int) -> OrganizationMembership | None:
    return db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.status == MembershipStatus.active,
        )
    )


def active_account_entitlement(db: Session, *, account_id: int, user_id: int) -> AccountEntitlement | None:
    return db.scalar(
        select(AccountEntitlement).where(
            AccountEntitlement.account_id == account_id,
            AccountEntitlement.user_id == user_id,
            AccountEntitlement.status == EntitlementStatus.active,
        )
    )


def accessible_account_ids(db: Session, user_id: int) -> list[int]:
    if _is_internal(db, user_id):
        return list(db.scalars(select(Account.id)).all())

    ids = set(
        db.scalars(
            select(Account.id).where(
                Account.user_id == user_id,
                Account.organization_id.is_(None),
            )
        ).all()
    )
    entitled_ids = db.scalars(
        select(AccountEntitlement.account_id)
        .join(Account, Account.id == AccountEntitlement.account_id)
        .where(
            AccountEntitlement.user_id == user_id,
            AccountEntitlement.can_view.is_(True),
            AccountEntitlement.status == EntitlementStatus.active,
            Account.organization_id.is_not(None),
        )
    ).all()
    ids.update(entitled_ids)
    return sorted(ids)


def list_accessible_accounts(db: Session, user_id: int) -> list[Account]:
    account_ids = accessible_account_ids(db, user_id)
    if not account_ids:
        return []
    return db.scalars(select(Account).where(Account.id.in_(account_ids)).order_by(Account.name)).all()


def account_with_access(
    db: Session,
    user_id: int,
    account_id: int,
    *,
    require_transact: bool = False,
    require_approve: bool = False,
) -> Account:
    account = db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if account.organization_id is None:
        if account.user_id == user_id or (_is_internal_account_manager(db, user_id) and not require_transact):
            return account
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if _is_internal_account_manager(db, user_id) and not require_transact:
        return account

    entitlement = active_account_entitlement(db, account_id=account_id, user_id=user_id)
    if not entitlement or not entitlement.can_view:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account access denied")
    if require_transact and not entitlement.can_transact:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account transaction access denied")
    if require_approve and not entitlement.can_approve:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account approval access denied")
    return account


def owned_account(db: Session, user_id: int, account_id: int) -> Account:
    return account_with_access(db, user_id, account_id)


def create_account(db: Session, user_id: int, payload: AccountCreate) -> Account:
    values = payload.model_dump()
    organization_id = values.get("organization_id")
    if organization_id is not None:
        organization = db.get(Organization, organization_id)
        if not organization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        if organization.status != OrganizationStatus.active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization is not active")
        membership = _active_membership(db, organization_id=organization_id, user_id=user_id)
        if not membership and not _is_internal_account_manager(db, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization membership required")
        if membership and membership.role not in ORG_ACCOUNT_MANAGERS and not _is_internal_account_manager(db, user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization account management access denied")

    account = Account(user_id=user_id, **values)
    db.add(account)
    db.flush()
    if organization_id is not None:
        exists = active_account_entitlement(db, account_id=account.id, user_id=user_id)
        if not exists:
            db.add(
                AccountEntitlement(
                    organization_id=organization_id,
                    account_id=account.id,
                    user_id=user_id,
                    can_view=True,
                    can_transact=True,
                    can_approve=True,
                    status=EntitlementStatus.active,
                )
            )
    db.commit()
    db.refresh(account)
    return account


def update_account(db: Session, account: Account, payload: AccountUpdate) -> Account:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, key, value)
    db.commit()
    db.refresh(account)
    return account
