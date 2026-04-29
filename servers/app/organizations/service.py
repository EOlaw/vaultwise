from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..accounts.models import Account
from ..iam.policies import INTERNAL_ROLES
from ..iam.service import user_role_names
from ..users.models import User
from .models import (
    AccountEntitlement,
    EntitlementStatus,
    MembershipRole,
    MembershipStatus,
    Organization,
    OrganizationMembership,
    OrganizationStatus,
)
from .schemas import EntitlementCreate, EntitlementUpdate, MembershipCreate, MembershipUpdate, OrganizationCreate, OrganizationUpdate


ORG_MANAGE_ROLES = {MembershipRole.owner, MembershipRole.admin}
ORG_TRANSFER_ROLES = {MembershipRole.owner, MembershipRole.admin, MembershipRole.operator}
ORG_APPROVER_ROLES = {MembershipRole.owner, MembershipRole.admin, MembershipRole.approver}
INTERNAL_MANAGE_ROLES = {"super_admin", "bank_admin"}


def _not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def active_membership(db: Session, *, organization_id: int, user_id: int) -> OrganizationMembership | None:
    return db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.status == MembershipStatus.active,
        )
    )


def is_internal_user(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & INTERNAL_ROLES)


def can_manage_internally(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & INTERNAL_MANAGE_ROLES)


def list_accessible_organizations(db: Session, user: User) -> list[Organization]:
    if is_internal_user(db, user.id):
        return db.scalars(select(Organization).order_by(Organization.name)).all()
    return db.scalars(
        select(Organization)
        .join(OrganizationMembership, OrganizationMembership.organization_id == Organization.id)
        .where(
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.status == MembershipStatus.active,
        )
        .order_by(Organization.name)
    ).all()


def require_organization_access(db: Session, user: User, organization_id: int, *, manage: bool = False) -> Organization:
    organization = db.get(Organization, organization_id)
    if not organization:
        raise _not_found("Organization")
    if can_manage_internally(db, user.id):
        return organization
    if organization.status != OrganizationStatus.active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization is not active")
    membership = active_membership(db, organization_id=organization_id, user_id=user.id)
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization access denied")
    if manage and membership.role not in ORG_MANAGE_ROLES:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization management access denied")
    return organization


def create_organization(db: Session, user: User, payload: OrganizationCreate) -> Organization:
    organization = Organization(created_by_user_id=user.id, **payload.model_dump())
    db.add(organization)
    db.flush()
    db.add(
        OrganizationMembership(
            organization_id=organization.id,
            user_id=user.id,
            role=MembershipRole.owner,
            status=MembershipStatus.active,
            title="Owner",
            can_invite_members=True,
        )
    )
    db.commit()
    db.refresh(organization)
    return organization


def update_organization(db: Session, organization: Organization, payload: OrganizationUpdate) -> Organization:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(organization, key, value)
    db.commit()
    db.refresh(organization)
    return organization


def list_memberships(db: Session, user: User, organization_id: int) -> list[OrganizationMembership]:
    require_organization_access(db, user, organization_id)
    return db.scalars(
        select(OrganizationMembership)
        .where(OrganizationMembership.organization_id == organization_id)
        .order_by(OrganizationMembership.role, OrganizationMembership.id)
    ).all()


def create_membership(db: Session, actor: User, organization_id: int, payload: MembershipCreate) -> OrganizationMembership:
    require_organization_access(db, actor, organization_id, manage=True)
    if not db.get(User, payload.user_id):
        raise _not_found("User")
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == payload.user_id,
        )
    )
    values = payload.model_dump()
    if membership:
        for key, value in values.items():
            setattr(membership, key, value)
        membership.status = MembershipStatus.active
    else:
        membership = OrganizationMembership(organization_id=organization_id, status=MembershipStatus.active, **values)
        db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def _active_owner_count(db: Session, organization_id: int) -> int:
    return int(
        db.scalar(
            select(func.count(OrganizationMembership.id)).where(
                OrganizationMembership.organization_id == organization_id,
                OrganizationMembership.role == MembershipRole.owner,
                OrganizationMembership.status == MembershipStatus.active,
            )
        )
        or 0
    )


def update_membership(db: Session, actor: User, organization_id: int, membership_id: int, payload: MembershipUpdate) -> OrganizationMembership:
    require_organization_access(db, actor, organization_id, manage=True)
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.id == membership_id,
            OrganizationMembership.organization_id == organization_id,
        )
    )
    if not membership:
        raise _not_found("Membership")
    updates = payload.model_dump(exclude_unset=True)
    owner_is_being_removed = membership.role == MembershipRole.owner and (
        updates.get("role") not in {None, MembershipRole.owner}
        or updates.get("status") in {MembershipStatus.suspended, MembershipStatus.removed}
    )
    if owner_is_being_removed and _active_owner_count(db, organization_id) <= 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Organization must retain at least one active owner")
    for key, value in updates.items():
        setattr(membership, key, value)
    db.commit()
    db.refresh(membership)
    return membership


def list_entitlements(db: Session, user: User, organization_id: int) -> list[AccountEntitlement]:
    require_organization_access(db, user, organization_id)
    return db.scalars(
        select(AccountEntitlement)
        .where(AccountEntitlement.organization_id == organization_id)
        .order_by(AccountEntitlement.account_id, AccountEntitlement.user_id)
    ).all()


def upsert_entitlement(db: Session, actor: User, organization_id: int, payload: EntitlementCreate) -> AccountEntitlement:
    require_organization_access(db, actor, organization_id, manage=True)
    account = db.get(Account, payload.account_id)
    if not account or account.organization_id != organization_id:
        raise _not_found("Account")
    if not active_membership(db, organization_id=organization_id, user_id=payload.user_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User must be an active organization member before account access is granted")
    entitlement = db.scalar(
        select(AccountEntitlement).where(
            AccountEntitlement.organization_id == organization_id,
            AccountEntitlement.account_id == payload.account_id,
            AccountEntitlement.user_id == payload.user_id,
        )
    )
    values = payload.model_dump()
    if entitlement:
        for key, value in values.items():
            setattr(entitlement, key, value)
        entitlement.status = EntitlementStatus.active
        entitlement.revoked_at = None
    else:
        entitlement = AccountEntitlement(organization_id=organization_id, status=EntitlementStatus.active, **values)
        db.add(entitlement)
    db.commit()
    db.refresh(entitlement)
    return entitlement


def update_entitlement(db: Session, actor: User, organization_id: int, entitlement_id: int, payload: EntitlementUpdate) -> AccountEntitlement:
    require_organization_access(db, actor, organization_id, manage=True)
    entitlement = db.scalar(
        select(AccountEntitlement).where(
            AccountEntitlement.id == entitlement_id,
            AccountEntitlement.organization_id == organization_id,
        )
    )
    if not entitlement:
        raise _not_found("Entitlement")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(entitlement, key, value)
    if updates.get("status") == EntitlementStatus.revoked and entitlement.revoked_at is None:
        entitlement.revoked_at = datetime.utcnow()
    if updates.get("status") == EntitlementStatus.active:
        entitlement.revoked_at = None
    db.commit()
    db.refresh(entitlement)
    return entitlement
