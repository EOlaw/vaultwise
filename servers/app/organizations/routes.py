from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..audit.service import record_audit
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .schemas import (
    EntitlementCreate,
    EntitlementRead,
    EntitlementUpdate,
    MembershipCreate,
    MembershipRead,
    MembershipUpdate,
    OrganizationCreate,
    OrganizationRead,
    OrganizationUpdate,
)
from .service import (
    create_membership,
    create_organization,
    list_accessible_organizations,
    list_entitlements,
    list_memberships,
    require_organization_access,
    update_entitlement,
    update_membership,
    update_organization,
    upsert_entitlement,
)


router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationRead])
def list_organizations(db: Session = Depends(get_db), user: User = Depends(require_permission("organizations:read"))):
    return list_accessible_organizations(db, user)


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create(
    payload: OrganizationCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("organizations:create")),
):
    organization = create_organization(db, user, payload)
    record_audit(db, action="ORGANIZATION_CREATED", actor_user_id=user.id, resource_type="organization", resource_id=organization.id, request=request)
    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("organizations:read"))):
    return require_organization_access(db, user, organization_id)


@router.patch("/{organization_id}", response_model=OrganizationRead)
def patch_organization(
    organization_id: int,
    payload: OrganizationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("organizations:update")),
):
    organization = update_organization(db, require_organization_access(db, user, organization_id, manage=True), payload)
    record_audit(db, action="ORGANIZATION_UPDATED", actor_user_id=user.id, resource_type="organization", resource_id=organization.id, request=request)
    return organization


@router.get("/{organization_id}/memberships", response_model=list[MembershipRead])
def memberships(organization_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("memberships:read"))):
    return list_memberships(db, user, organization_id)


@router.post("/{organization_id}/memberships", response_model=MembershipRead, status_code=status.HTTP_201_CREATED)
def add_membership(
    organization_id: int,
    payload: MembershipCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("memberships:manage")),
):
    membership = create_membership(db, user, organization_id, payload)
    record_audit(
        db,
        action="ORGANIZATION_MEMBERSHIP_GRANTED",
        actor_user_id=user.id,
        resource_type="organization_membership",
        resource_id=membership.id,
        request=request,
        metadata={"organization_id": organization_id, "member_user_id": membership.user_id, "role": membership.role.value},
    )
    return membership


@router.patch("/{organization_id}/memberships/{membership_id}", response_model=MembershipRead)
def patch_membership(
    organization_id: int,
    membership_id: int,
    payload: MembershipUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("memberships:manage")),
):
    membership = update_membership(db, user, organization_id, membership_id, payload)
    record_audit(
        db,
        action="ORGANIZATION_MEMBERSHIP_UPDATED",
        actor_user_id=user.id,
        resource_type="organization_membership",
        resource_id=membership.id,
        request=request,
        metadata={"organization_id": organization_id, "member_user_id": membership.user_id, "role": membership.role.value},
    )
    return membership


@router.get("/{organization_id}/entitlements", response_model=list[EntitlementRead])
def entitlements(organization_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("entitlements:read"))):
    return list_entitlements(db, user, organization_id)


@router.post("/{organization_id}/entitlements", response_model=EntitlementRead, status_code=status.HTTP_201_CREATED)
def grant_entitlement(
    organization_id: int,
    payload: EntitlementCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("entitlements:manage")),
):
    entitlement = upsert_entitlement(db, user, organization_id, payload)
    record_audit(
        db,
        action="ACCOUNT_ENTITLEMENT_GRANTED",
        actor_user_id=user.id,
        resource_type="account_entitlement",
        resource_id=entitlement.id,
        request=request,
        metadata={"organization_id": organization_id, "account_id": entitlement.account_id, "member_user_id": entitlement.user_id},
    )
    return entitlement


@router.patch("/{organization_id}/entitlements/{entitlement_id}", response_model=EntitlementRead)
def patch_entitlement(
    organization_id: int,
    entitlement_id: int,
    payload: EntitlementUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("entitlements:manage")),
):
    entitlement = update_entitlement(db, user, organization_id, entitlement_id, payload)
    record_audit(
        db,
        action="ACCOUNT_ENTITLEMENT_UPDATED",
        actor_user_id=user.id,
        resource_type="account_entitlement",
        resource_id=entitlement.id,
        request=request,
        metadata={"organization_id": organization_id, "account_id": entitlement.account_id, "member_user_id": entitlement.user_id},
    )
    return entitlement
