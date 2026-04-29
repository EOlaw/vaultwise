from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..users.models import User
from .service import has_permission, record_policy_decision


INTERNAL_ROLES = {"super_admin", "bank_admin", "compliance_officer", "risk_manager", "support_agent"}


def assert_permission(db: Session, user: User, permission: str) -> None:
    if has_permission(db, user, permission):
        record_policy_decision(db, user=user, permission=permission, decision="allow", reason="permission granted")
        return
    record_policy_decision(db, user=user, permission=permission, decision="deny", reason="missing permission")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permission: {permission}")


def assert_owner_or_internal(
    db: Session,
    user: User,
    *,
    resource_user_id: int,
    permission: str,
    resource_type: str,
    resource_id: int | str,
) -> None:
    if user.id == resource_user_id:
        record_policy_decision(
            db,
            user=user,
            permission=permission,
            resource_type=resource_type,
            resource_id=resource_id,
            decision="allow",
            reason="resource owner",
        )
        return
    if has_permission(db, user, permission):
        record_policy_decision(
            db,
            user=user,
            permission=permission,
            resource_type=resource_type,
            resource_id=resource_id,
            decision="allow",
            reason="internal permission",
        )
        return
    record_policy_decision(
        db,
        user=user,
        permission=permission,
        resource_type=resource_type,
        resource_id=resource_id,
        decision="deny",
        reason="not owner and missing internal permission",
    )
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied by banking policy")
