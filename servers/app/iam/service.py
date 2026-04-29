from sqlalchemy import select
from sqlalchemy.orm import Session
from ..users.models import User, UserRole
from .defaults import PERMISSIONS, ROLE_PERMISSIONS
from .models import Permission, PolicyDecision, Role, RolePermission, UserRoleAssignment


def bootstrap_iam(db: Session) -> None:
    permissions_by_code: dict[str, Permission] = {}
    for code, description in PERMISSIONS.items():
        permission = db.scalar(select(Permission).where(Permission.code == code))
        if not permission:
            permission = Permission(code=code, description=description)
            db.add(permission)
            db.flush()
        permissions_by_code[code] = permission

    roles_by_name: dict[str, Role] = {}
    for name, permission_codes in ROLE_PERMISSIONS.items():
        role = db.scalar(select(Role).where(Role.name == name))
        if not role:
            role = Role(name=name, description=f"{name.replace('_', ' ').title()} banking role")
            db.add(role)
            db.flush()
        roles_by_name[name] = role
        for code in permission_codes:
            exists = db.scalar(select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == permissions_by_code[code].id,
            ))
            if not exists:
                db.add(RolePermission(role_id=role.id, permission_id=permissions_by_code[code].id))
    db.commit()


def assign_role(db: Session, *, user_id: int, role_name: str, assigned_by_user_id: int | None = None) -> None:
    role = db.scalar(select(Role).where(Role.name == role_name))
    if not role:
        raise ValueError(f"Unknown role: {role_name}")
    exists = db.scalar(select(UserRoleAssignment).where(
        UserRoleAssignment.user_id == user_id,
        UserRoleAssignment.role_id == role.id,
    ))
    if not exists:
        db.add(UserRoleAssignment(user_id=user_id, role_id=role.id, assigned_by_user_id=assigned_by_user_id))
        db.commit()


def sync_legacy_user_role(db: Session, user: User) -> None:
    bootstrap_iam(db)
    if user_role_names(db, user.id):
        return
    role_name = "super_admin" if user.role == UserRole.admin else "customer"
    assign_role(db, user_id=user.id, role_name=role_name)


def user_role_names(db: Session, user_id: int) -> set[str]:
    rows = db.execute(
        select(Role.name)
        .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
        .where(UserRoleAssignment.user_id == user_id)
    ).all()
    return {row[0] for row in rows}


def user_permissions(db: Session, user: User) -> set[str]:
    roles = user_role_names(db, user.id)
    if not roles:
        sync_legacy_user_role(db, user)
        roles = user_role_names(db, user.id)
    rows = db.execute(
        select(Permission.code)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .where(Role.name.in_(roles))
    ).all()
    return {row[0] for row in rows}


def has_permission(db: Session, user: User, permission: str) -> bool:
    return permission in user_permissions(db, user)


def record_policy_decision(
    db: Session,
    *,
    user: User | None,
    permission: str,
    decision: str,
    reason: str,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
) -> None:
    db.add(PolicyDecision(
        user_id=user.id if user else None,
        permission=permission,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        decision=decision,
        reason=reason,
    ))
    db.commit()
