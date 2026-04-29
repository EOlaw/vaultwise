import json
from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..accounts.service import accessible_account_ids
from ..iam.policies import INTERNAL_ROLES
from ..iam.service import user_role_names
from ..organizations.models import MembershipRole, MembershipStatus, OrganizationMembership
from ..organizations.service import require_organization_access
from ..transfers.models import Transfer, TransferEvent, TransferStatus
from ..users.models import User
from .models import ApprovalDecision, ApprovalDecisionType, ApprovalPolicy, ApprovalRequest, ApprovalStatus, ApprovalTargetType
from .schemas import ApprovalPolicyCreate, ApprovalPolicyUpdate


DEFAULT_BUSINESS_APPROVAL_THRESHOLD = Decimal("1000.00")
POLICY_MANAGER_ROLES = {"super_admin", "bank_admin"}


def _is_internal(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & INTERNAL_ROLES)


def _can_manage_global_policies(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & POLICY_MANAGER_ROLES)


def _active_org_ids(db: Session, user_id: int) -> list[int]:
    return list(
        db.scalars(
            select(OrganizationMembership.organization_id).where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.status == MembershipStatus.active,
            )
        ).all()
    )


def _user_can_approve_org(db: Session, user: User, organization_id: int | None) -> bool:
    if _is_internal(db, user.id):
        return True
    if organization_id is None:
        return False
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.status == MembershipStatus.active,
        )
    )
    return bool(membership and membership.role in {MembershipRole.owner, MembershipRole.admin, MembershipRole.approver})


def _matching_policies(db: Session, transfer: Transfer) -> list[ApprovalPolicy]:
    return db.scalars(
        select(ApprovalPolicy).where(
            ApprovalPolicy.is_active.is_(True),
            or_(ApprovalPolicy.organization_id == transfer.organization_id, ApprovalPolicy.organization_id.is_(None)),
            or_(ApprovalPolicy.transfer_type == transfer.transfer_type.value, ApprovalPolicy.transfer_type.is_(None)),
            ApprovalPolicy.min_amount <= transfer.amount,
        )
    ).all()


def transfer_approval_requirement(db: Session, transfer: Transfer, *, requester_can_approve: bool, force_approval: bool = False) -> tuple[int, bool, str]:
    policies = _matching_policies(db, transfer)
    if policies:
        required = max(policy.required_approvals for policy in policies)
        separate = any(policy.require_separate_approver for policy in policies)
        names = ", ".join(sorted(policy.name for policy in policies))
        return required, separate, f"Matched approval policy: {names}"
    if force_approval:
        return 1, True, "Risk review requires approval"
    if transfer.organization_id is not None and (Decimal(transfer.amount) >= DEFAULT_BUSINESS_APPROVAL_THRESHOLD or not requester_can_approve):
        return 1, True, "Business transfer requires dual control approval"
    return 0, False, "No approval required"


def ensure_transfer_approval_request(
    db: Session,
    transfer: Transfer,
    *,
    requested_by_user_id: int,
    required_approvals: int,
    require_separate_approver: bool,
    reason: str,
    metadata: dict | None = None,
) -> ApprovalRequest:
    existing = db.scalar(select(ApprovalRequest).where(ApprovalRequest.transfer_id == transfer.id))
    if existing:
        existing.status = ApprovalStatus.pending
        existing.required_approvals = required_approvals
        existing.require_separate_approver = require_separate_approver
        existing.reason = reason
        existing.metadata_json = json.dumps(metadata or {}, sort_keys=True)
        existing.completed_at = None
        return existing
    approval = ApprovalRequest(
        organization_id=transfer.organization_id,
        target_type=ApprovalTargetType.transfer,
        transfer_id=transfer.id,
        requested_by_user_id=requested_by_user_id,
        status=ApprovalStatus.pending,
        required_approvals=required_approvals,
        current_approvals=0,
        require_separate_approver=require_separate_approver,
        reason=reason,
        metadata_json=json.dumps(metadata or {}, sort_keys=True),
    )
    db.add(approval)
    return approval


def _approval_access_query(db: Session, user: User):
    if _is_internal(db, user.id):
        return select(ApprovalRequest)
    clauses = [ApprovalRequest.requested_by_user_id == user.id]
    org_ids = _active_org_ids(db, user.id)
    account_ids = accessible_account_ids(db, user.id)
    if org_ids:
        clauses.append(ApprovalRequest.organization_id.in_(org_ids))
    if account_ids:
        clauses.append(ApprovalRequest.transfer_id.in_(select(Transfer.id).where(Transfer.from_account_id.in_(account_ids))))
    return select(ApprovalRequest).where(or_(*clauses))


def list_approval_requests(db: Session, user: User, status_filter: ApprovalStatus | None = None) -> list[ApprovalRequest]:
    query = _approval_access_query(db, user)
    if status_filter is not None:
        query = query.where(ApprovalRequest.status == status_filter)
    return db.scalars(query.order_by(ApprovalRequest.created_at.desc(), ApprovalRequest.id.desc())).unique().all()


def get_approval_request_with_access(db: Session, user: User, approval_id: int) -> ApprovalRequest:
    approval = db.scalar(_approval_access_query(db, user).where(ApprovalRequest.id == approval_id))
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval request not found")
    return approval


def _record_transfer_event(
    db: Session,
    transfer: Transfer,
    *,
    actor_user_id: int,
    event_type: str,
    from_status: TransferStatus,
    to_status: TransferStatus,
    metadata: dict | None = None,
) -> None:
    db.add(
        TransferEvent(
            transfer_id=transfer.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            from_status=from_status.value,
            to_status=to_status.value,
            metadata_json=json.dumps(metadata or {}, sort_keys=True),
        )
    )


def _assert_can_decide(db: Session, user: User, approval: ApprovalRequest, transfer: Transfer) -> None:
    if approval.require_separate_approver and approval.requested_by_user_id == user.id and not _is_internal(db, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="A separate approver is required")
    if not _user_can_approve_org(db, user, transfer.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approval access denied")
    if transfer.organization_id is not None:
        from ..accounts.service import account_with_access

        account_with_access(db, user.id, transfer.from_account_id, require_approve=True)


def approve_approval_request(db: Session, user: User, approval_id: int, notes: str | None = None) -> ApprovalRequest:
    approval = get_approval_request_with_access(db, user, approval_id)
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approval request is not pending")
    transfer = db.get(Transfer, approval.transfer_id)
    if not transfer or transfer.status != TransferStatus.pending_approval:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transfer is not pending approval")
    _assert_can_decide(db, user, approval, transfer)
    existing_decision = db.scalar(
        select(ApprovalDecision).where(
            ApprovalDecision.approval_request_id == approval.id,
            ApprovalDecision.actor_user_id == user.id,
        )
    )
    if existing_decision:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User has already decided this approval")
    db.add(
        ApprovalDecision(
            approval_request_id=approval.id,
            actor_user_id=user.id,
            decision=ApprovalDecisionType.approved,
            notes=notes,
        )
    )
    approval.current_approvals = int(
        db.scalar(
            select(func.count(ApprovalDecision.id)).where(
                ApprovalDecision.approval_request_id == approval.id,
                ApprovalDecision.decision == ApprovalDecisionType.approved,
            )
        )
        or 0
    ) + 1
    if approval.current_approvals >= approval.required_approvals:
        previous = transfer.status
        approval.status = ApprovalStatus.approved
        approval.completed_at = datetime.utcnow()
        if transfer.scheduled_for and transfer.scheduled_for > date.today():
            transfer.status = TransferStatus.scheduled
            _record_transfer_event(db, transfer, actor_user_id=user.id, event_type="APPROVED", from_status=previous, to_status=transfer.status)
        else:
            from ..transfers.service import _post_transfer

            _post_transfer(db, transfer, user.id)
    db.commit()
    db.refresh(approval)
    return approval


def reject_approval_request(db: Session, user: User, approval_id: int, notes: str | None = None) -> ApprovalRequest:
    approval = get_approval_request_with_access(db, user, approval_id)
    if approval.status != ApprovalStatus.pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approval request is not pending")
    transfer = db.get(Transfer, approval.transfer_id)
    if not transfer or transfer.status != TransferStatus.pending_approval:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transfer is not pending approval")
    _assert_can_decide(db, user, approval, transfer)
    existing_decision = db.scalar(
        select(ApprovalDecision).where(
            ApprovalDecision.approval_request_id == approval.id,
            ApprovalDecision.actor_user_id == user.id,
        )
    )
    if existing_decision:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User has already decided this approval")
    db.add(
        ApprovalDecision(
            approval_request_id=approval.id,
            actor_user_id=user.id,
            decision=ApprovalDecisionType.rejected,
            notes=notes,
        )
    )
    previous = transfer.status
    transfer.status = TransferStatus.rejected
    approval.status = ApprovalStatus.rejected
    approval.completed_at = datetime.utcnow()
    _record_transfer_event(db, transfer, actor_user_id=user.id, event_type="REJECTED", from_status=previous, to_status=TransferStatus.rejected, metadata={"notes": notes})
    from ..notifications.service import notify_transfer_rejected

    notify_transfer_rejected(db, transfer, notes)
    db.commit()
    db.refresh(approval)
    return approval


def list_policies(db: Session, user: User, organization_id: int | None = None) -> list[ApprovalPolicy]:
    query = select(ApprovalPolicy)
    if organization_id is not None:
        require_organization_access(db, user, organization_id)
        query = query.where(ApprovalPolicy.organization_id == organization_id)
    elif not _can_manage_global_policies(db, user.id):
        org_ids = _active_org_ids(db, user.id)
        query = query.where(ApprovalPolicy.organization_id.in_(org_ids) if org_ids else ApprovalPolicy.id == -1)
    return db.scalars(query.order_by(ApprovalPolicy.organization_id, ApprovalPolicy.min_amount.desc())).all()


def create_policy(db: Session, user: User, payload: ApprovalPolicyCreate) -> ApprovalPolicy:
    if payload.organization_id is None:
        if not _can_manage_global_policies(db, user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Global approval policies require bank admin access")
    else:
        require_organization_access(db, user, payload.organization_id, manage=True)
    policy = ApprovalPolicy(created_by_user_id=user.id, **payload.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def update_policy(db: Session, user: User, policy_id: int, payload: ApprovalPolicyUpdate) -> ApprovalPolicy:
    policy = db.get(ApprovalPolicy, policy_id)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval policy not found")
    if policy.organization_id is None:
        if not _can_manage_global_policies(db, user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Global approval policies require bank admin access")
    else:
        require_organization_access(db, user, policy.organization_id, manage=True)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(policy, key, value)
    db.commit()
    db.refresh(policy)
    return policy
