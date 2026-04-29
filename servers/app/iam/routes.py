from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..audit.service import record_audit
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .models import Permission, PolicyDecision, Role
from .schemas import AssignRoleRequest, PermissionRead, PolicyDecisionRead, RoleRead
from .service import assign_role, bootstrap_iam


router = APIRouter(prefix="/iam", tags=["iam"])


@router.get("/roles", response_model=list[RoleRead])
def list_roles(db: Session = Depends(get_db), _: User = Depends(require_permission("iam:manage"))):
    bootstrap_iam(db)
    return db.scalars(select(Role).order_by(Role.name)).all()


@router.get("/permissions", response_model=list[PermissionRead])
def list_permissions(db: Session = Depends(get_db), _: User = Depends(require_permission("iam:manage"))):
    bootstrap_iam(db)
    return db.scalars(select(Permission).order_by(Permission.code)).all()


@router.post("/assign-role", status_code=204)
def assign_role_to_user(
    payload: AssignRoleRequest,
    db: Session = Depends(get_db),
    actor: User = Depends(require_permission("iam:manage")),
):
    bootstrap_iam(db)
    assign_role(db, user_id=payload.user_id, role_name=payload.role_name, assigned_by_user_id=actor.id)
    record_audit(db, action="ROLE_ASSIGNED", actor_user_id=actor.id, resource_type="user", resource_id=payload.user_id, metadata={"role": payload.role_name})
    return None


@router.get("/policy-decisions", response_model=list[PolicyDecisionRead])
def policy_decisions(db: Session = Depends(get_db), _: User = Depends(require_permission("audit:read"))):
    return db.scalars(select(PolicyDecision).order_by(PolicyDecision.created_at.desc()).limit(200)).all()
