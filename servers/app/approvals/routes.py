from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..audit.service import record_audit
from ..auth.idempotency import begin_idempotent_request, finalize_idempotent_request
from ..auth.models import UserSession
from ..database import get_db
from ..dependencies import require_permission, require_step_up
from ..users.models import User
from .models import ApprovalStatus
from .schemas import ApprovalDecisionRequest, ApprovalPolicyCreate, ApprovalPolicyRead, ApprovalPolicyUpdate, ApprovalRequestRead
from .service import (
    approve_approval_request,
    create_policy,
    get_approval_request_with_access,
    list_approval_requests,
    list_policies,
    reject_approval_request,
    update_policy,
)


router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("/policies", response_model=list[ApprovalPolicyRead])
def approval_policies(
    organization_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("approvals:read")),
):
    return list_policies(db, user, organization_id)


@router.post("/policies", response_model=ApprovalPolicyRead, status_code=status.HTTP_201_CREATED)
def create_approval_policy(
    payload: ApprovalPolicyCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("approvals:manage")),
    _: UserSession = Depends(require_step_up),
):
    policy = create_policy(db, user, payload)
    record_audit(db, action="APPROVAL_POLICY_CREATED", actor_user_id=user.id, resource_type="approval_policy", resource_id=policy.id, request=request)
    return policy


@router.patch("/policies/{policy_id}", response_model=ApprovalPolicyRead)
def patch_approval_policy(
    policy_id: int,
    payload: ApprovalPolicyUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("approvals:manage")),
    _: UserSession = Depends(require_step_up),
):
    policy = update_policy(db, user, policy_id, payload)
    record_audit(db, action="APPROVAL_POLICY_UPDATED", actor_user_id=user.id, resource_type="approval_policy", resource_id=policy.id, request=request)
    return policy


@router.get("", response_model=list[ApprovalRequestRead])
def approval_queue(
    status_filter: ApprovalStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("approvals:read")),
):
    return list_approval_requests(db, user, status_filter)


@router.get("/{approval_id}", response_model=ApprovalRequestRead)
def get_approval(approval_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("approvals:read"))):
    return get_approval_request_with_access(db, user, approval_id)


@router.post("/{approval_id}/approve", response_model=ApprovalRequestRead)
def approve(
    approval_id: int,
    payload: ApprovalDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("approvals:decide")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"approval_id": approval_id, "decision": "approve", "payload": payload.model_dump(mode="json")})
    if idempotency.replay:
        return get_approval_request_with_access(db, user, int(idempotency.record.resource_id))
    approval = approve_approval_request(db, user, approval_id, payload.notes)
    finalize_idempotent_request(db, idempotency, resource_type="approval_request", resource_id=approval.id)
    record_audit(db, action="APPROVAL_APPROVED", actor_user_id=user.id, resource_type="approval_request", resource_id=approval.id, request=request)
    return approval


@router.post("/{approval_id}/reject", response_model=ApprovalRequestRead)
def reject(
    approval_id: int,
    payload: ApprovalDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("approvals:decide")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"approval_id": approval_id, "decision": "reject", "payload": payload.model_dump(mode="json")})
    if idempotency.replay:
        return get_approval_request_with_access(db, user, int(idempotency.record.resource_id))
    approval = reject_approval_request(db, user, approval_id, payload.notes)
    finalize_idempotent_request(db, idempotency, resource_type="approval_request", resource_id=approval.id)
    record_audit(db, action="APPROVAL_REJECTED", actor_user_id=user.id, resource_type="approval_request", resource_id=approval.id, request=request)
    return approval
