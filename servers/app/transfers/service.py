import json
from datetime import date, datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..accounts.models import Account, AccountType
from ..accounts.service import account_with_access, active_account_entitlement, accessible_account_ids
from ..iam.policies import INTERNAL_ROLES
from ..iam.service import user_role_names
from ..organizations.models import MembershipRole, MembershipStatus, OrganizationMembership
from ..organizations.service import require_organization_access
from ..transactions.models import Transaction, TransactionType
from ..users.models import User
from .models import Beneficiary, BeneficiaryStatus, BeneficiaryType, Transfer, TransferEvent, TransferStatus, TransferType
from .schemas import BeneficiaryCreate, BeneficiaryUpdate, TransferCreate


TRANSFER_ORG_ROLES = {MembershipRole.owner, MembershipRole.admin, MembershipRole.operator, MembershipRole.approver}
POSTABLE_ACCOUNT_TYPES = {AccountType.cash, AccountType.bank}
BUSINESS_APPROVAL_THRESHOLD = Decimal("1000.00")
CANCELLABLE_STATUSES = {TransferStatus.draft, TransferStatus.pending_approval, TransferStatus.scheduled}


def _is_internal(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & INTERNAL_ROLES)


def _active_org_ids(db: Session, user_id: int) -> list[int]:
    return list(
        db.scalars(
            select(OrganizationMembership.organization_id).where(
                OrganizationMembership.user_id == user_id,
                OrganizationMembership.status == MembershipStatus.active,
            )
        ).all()
    )


def _require_org_transfer_access(db: Session, user: User, organization_id: int) -> None:
    require_organization_access(db, user, organization_id)
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.status == MembershipStatus.active,
        )
    )
    if membership and membership.role in TRANSFER_ORG_ROLES:
        return
    if _is_internal(db, user.id):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization transfer access denied")


def _record_event(
    db: Session,
    transfer: Transfer,
    *,
    actor_user_id: int | None,
    event_type: str,
    from_status: TransferStatus | None = None,
    to_status: TransferStatus | None = None,
    metadata: dict | None = None,
) -> TransferEvent:
    event = TransferEvent(
        transfer_id=transfer.id,
        actor_user_id=actor_user_id,
        event_type=event_type,
        from_status=from_status.value if from_status else None,
        to_status=to_status.value if to_status else None,
        metadata_json=json.dumps(metadata or {}, sort_keys=True),
    )
    db.add(event)
    return event


def _beneficiary_access_query(db: Session, user: User):
    if _is_internal(db, user.id):
        return select(Beneficiary)
    org_ids = _active_org_ids(db, user.id)
    if org_ids:
        return select(Beneficiary).where(or_(Beneficiary.owner_user_id == user.id, Beneficiary.organization_id.in_(org_ids)))
    return select(Beneficiary).where(Beneficiary.owner_user_id == user.id)


def list_beneficiaries(db: Session, user: User, organization_id: int | None = None) -> list[Beneficiary]:
    query = _beneficiary_access_query(db, user)
    if organization_id is not None:
        require_organization_access(db, user, organization_id)
        query = query.where(Beneficiary.organization_id == organization_id)
    return db.scalars(query.order_by(Beneficiary.display_name)).all()


def _get_beneficiary_with_access(db: Session, user: User, beneficiary_id: int) -> Beneficiary:
    beneficiary = db.scalar(_beneficiary_access_query(db, user).where(Beneficiary.id == beneficiary_id))
    if not beneficiary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Beneficiary not found")
    return beneficiary


def create_beneficiary(db: Session, user: User, payload: BeneficiaryCreate) -> Beneficiary:
    if payload.organization_id is not None:
        _require_org_transfer_access(db, user, payload.organization_id)
    if payload.internal_account_id is not None:
        account_with_access(db, user.id, payload.internal_account_id)
    beneficiary = Beneficiary(owner_user_id=user.id, created_by_user_id=user.id, status=BeneficiaryStatus.active, **payload.model_dump())
    db.add(beneficiary)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


def update_beneficiary(db: Session, user: User, beneficiary_id: int, payload: BeneficiaryUpdate) -> Beneficiary:
    beneficiary = _get_beneficiary_with_access(db, user, beneficiary_id)
    if beneficiary.organization_id is not None:
        _require_org_transfer_access(db, user, beneficiary.organization_id)
    elif beneficiary.owner_user_id != user.id and not _is_internal(db, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Beneficiary access denied")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(beneficiary, key, value)
    db.commit()
    db.refresh(beneficiary)
    return beneficiary


def _validate_funding_account(db: Session, user: User, account: Account, amount: Decimal) -> None:
    if account.type not in POSTABLE_ACCOUNT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfers can only originate from cash or bank accounts")
    from ..ledger.service import assert_available_funds

    assert_available_funds(db, account, amount)
    if account.organization_id is not None:
        entitlement = active_account_entitlement(db, account_id=account.id, user_id=user.id)
        if entitlement and entitlement.daily_limit is not None and amount > Decimal(entitlement.daily_limit):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transfer exceeds daily entitlement limit")
        if entitlement and entitlement.monthly_limit is not None and amount > Decimal(entitlement.monthly_limit):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transfer exceeds monthly entitlement limit")


def _validate_transfer_destination(db: Session, user: User, payload: TransferCreate, organization_id: int | None) -> tuple[int | None, int | None]:
    if payload.transfer_type == TransferType.internal:
        if payload.to_account_id == payload.from_account_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer destination must differ from source account")
        to_account = account_with_access(db, user.id, int(payload.to_account_id))
        if organization_id is not None and to_account.organization_id not in {None, organization_id}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Destination account is outside the selected organization")
        return to_account.id, None

    beneficiary = _get_beneficiary_with_access(db, user, int(payload.beneficiary_id))
    if beneficiary.status != BeneficiaryStatus.active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Beneficiary is not active")
    if organization_id != beneficiary.organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Beneficiary ownership does not match transfer ownership")
    if payload.transfer_type == TransferType.external_ach and beneficiary.beneficiary_type != BeneficiaryType.external_ach:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ACH transfer requires an ACH beneficiary")
    if payload.transfer_type == TransferType.wire and beneficiary.beneficiary_type != BeneficiaryType.wire:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wire transfer requires a wire beneficiary")
    return None, beneficiary.id


def create_transfer(db: Session, user: User, payload: TransferCreate) -> Transfer:
    from_account = account_with_access(db, user.id, payload.from_account_id, require_transact=True)
    organization_id = payload.organization_id if payload.organization_id is not None else from_account.organization_id
    if from_account.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source account does not belong to the selected owner")
    if organization_id is not None:
        _require_org_transfer_access(db, user, organization_id)
    _validate_funding_account(db, user, from_account, payload.amount)
    to_account_id, beneficiary_id = _validate_transfer_destination(db, user, payload, organization_id)
    transfer = Transfer(
        organization_id=organization_id,
        created_by_user_id=user.id,
        from_account_id=from_account.id,
        to_account_id=to_account_id,
        beneficiary_id=beneficiary_id,
        transfer_type=payload.transfer_type,
        amount=payload.amount,
        currency=payload.currency.upper(),
        memo=payload.memo,
        scheduled_for=payload.scheduled_for,
        status=TransferStatus.draft,
    )
    db.add(transfer)
    db.flush()
    _record_event(db, transfer, actor_user_id=user.id, event_type="CREATED", to_status=TransferStatus.draft)
    db.commit()
    db.refresh(transfer)
    return transfer


def _transfer_access_query(db: Session, user: User):
    if _is_internal(db, user.id):
        return select(Transfer)
    account_ids = accessible_account_ids(db, user.id)
    org_ids = _active_org_ids(db, user.id)
    clauses = [Transfer.created_by_user_id == user.id]
    if account_ids:
        clauses.extend([Transfer.from_account_id.in_(account_ids), Transfer.to_account_id.in_(account_ids)])
    if org_ids:
        clauses.append(Transfer.organization_id.in_(org_ids))
    return select(Transfer).where(or_(*clauses))


def list_transfers(db: Session, user: User, status_filter: TransferStatus | None = None) -> list[Transfer]:
    query = _transfer_access_query(db, user)
    if status_filter is not None:
        query = query.where(Transfer.status == status_filter)
    return db.scalars(query.order_by(Transfer.created_at.desc(), Transfer.id.desc())).all()


def get_transfer_with_access(db: Session, user: User, transfer_id: int) -> Transfer:
    transfer = db.scalar(_transfer_access_query(db, user).where(Transfer.id == transfer_id))
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    return transfer


def _actor_can_approve_transfer(db: Session, user: User, transfer: Transfer) -> bool:
    if _is_internal(db, user.id):
        return True
    if transfer.organization_id is None:
        return transfer.created_by_user_id == user.id
    account_with_access(db, user.id, transfer.from_account_id, require_approve=True)
    return True


def _post_transfer(db: Session, transfer: Transfer, actor_user_id: int) -> None:
    if transfer.status == TransferStatus.posted:
        return
    now = datetime.utcnow()
    from_account = db.get(Account, transfer.from_account_id)
    if not from_account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source account not found")
    from ..ledger.service import assert_available_funds, record_transfer_ledger_entries

    assert_available_funds(db, from_account, Decimal(transfer.amount), transfer=transfer)
    db.add(
        Transaction(
            user_id=transfer.created_by_user_id,
            account_id=transfer.from_account_id,
            type=TransactionType.transfer_out,
            amount=transfer.amount,
            occurred_on=date.today(),
            category="Transfer",
            notes=transfer.memo,
        )
    )
    if transfer.transfer_type == TransferType.internal and transfer.to_account_id is not None:
        to_account = db.get(Account, transfer.to_account_id)
        if not to_account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destination account not found")
        db.add(
            Transaction(
                user_id=to_account.user_id,
                account_id=to_account.id,
                type=TransactionType.transfer_in,
                amount=transfer.amount,
                occurred_on=date.today(),
                category="Transfer",
                notes=transfer.memo,
            )
        )
    previous = transfer.status
    transfer.status = TransferStatus.posted
    transfer.posted_at = now
    record_transfer_ledger_entries(db, transfer, actor_user_id=actor_user_id)
    _record_event(db, transfer, actor_user_id=actor_user_id, event_type="POSTED", from_status=previous, to_status=TransferStatus.posted)
    from ..notifications.service import notify_transfer_posted

    notify_transfer_posted(db, transfer)


def _requires_business_approval(db: Session, user: User, transfer: Transfer) -> bool:
    if transfer.organization_id is None:
        return False
    entitlement = active_account_entitlement(db, account_id=transfer.from_account_id, user_id=user.id)
    lacks_approval = not entitlement or not entitlement.can_approve
    return lacks_approval or Decimal(transfer.amount) >= BUSINESS_APPROVAL_THRESHOLD


def _requester_can_self_approve(db: Session, user: User, transfer: Transfer) -> bool:
    if _is_internal(db, user.id):
        return True
    if transfer.organization_id is None:
        return True
    entitlement = active_account_entitlement(db, account_id=transfer.from_account_id, user_id=user.id)
    return bool(entitlement and entitlement.can_approve)


def submit_transfer(db: Session, user: User, transfer_id: int) -> Transfer:
    transfer = get_transfer_with_access(db, user, transfer_id)
    if transfer.status != TransferStatus.draft:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only draft transfers can be submitted")
    from_account = account_with_access(db, user.id, transfer.from_account_id, require_transact=True)
    _validate_funding_account(db, user, from_account, Decimal(transfer.amount))
    previous = transfer.status
    from ..approvals.service import ensure_transfer_approval_request, transfer_approval_requirement
    from ..risk.service import alerts_require_approval, screen_transfer

    risk_alerts = screen_transfer(db, transfer, user)
    risk_requires_approval = alerts_require_approval(risk_alerts)
    required_approvals, separate_approver, approval_reason = transfer_approval_requirement(
        db,
        transfer,
        requester_can_approve=_requester_can_self_approve(db, user, transfer),
        force_approval=risk_requires_approval,
    )
    if required_approvals > 0:
        transfer.status = TransferStatus.pending_approval
        metadata = {"risk_alert_ids": [alert.id for alert in risk_alerts], "approval_reason": approval_reason}
        _record_event(db, transfer, actor_user_id=user.id, event_type="SUBMITTED", from_status=previous, to_status=transfer.status, metadata=metadata)
        from ..ledger.service import create_hold_for_transfer

        create_hold_for_transfer(db, transfer, actor_user_id=user.id, reason=approval_reason)
        ensure_transfer_approval_request(
            db,
            transfer,
            requested_by_user_id=user.id,
            required_approvals=required_approvals,
            require_separate_approver=separate_approver,
            reason=approval_reason,
            metadata=metadata,
        )
        from ..notifications.service import notify_transfer_pending_approval

        notify_transfer_pending_approval(db, transfer)
    elif transfer.scheduled_for and transfer.scheduled_for > date.today():
        transfer.status = TransferStatus.scheduled
        _record_event(db, transfer, actor_user_id=user.id, event_type="SCHEDULED", from_status=previous, to_status=transfer.status)
        from ..ledger.service import create_hold_for_transfer

        create_hold_for_transfer(db, transfer, actor_user_id=user.id, reason="Scheduled transfer hold")
    else:
        _post_transfer(db, transfer, user.id)
    db.commit()
    db.refresh(transfer)
    return transfer


def approve_transfer(db: Session, user: User, transfer_id: int) -> Transfer:
    transfer = get_transfer_with_access(db, user, transfer_id)
    if transfer.status != TransferStatus.pending_approval:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only pending transfers can be approved")
    from ..approvals.models import ApprovalRequest, ApprovalStatus
    from ..approvals.service import approve_approval_request

    approval = db.scalar(select(ApprovalRequest).where(ApprovalRequest.transfer_id == transfer.id, ApprovalRequest.status == ApprovalStatus.pending))
    if approval:
        approve_approval_request(db, user, approval.id)
        db.refresh(transfer)
        return transfer
    if transfer.organization_id is not None and transfer.created_by_user_id == user.id and not _is_internal(db, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Business transfers require a separate approver")
    if not _actor_can_approve_transfer(db, user, transfer):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Transfer approval access denied")
    previous = transfer.status
    if transfer.scheduled_for and transfer.scheduled_for > date.today():
        transfer.status = TransferStatus.scheduled
        _record_event(db, transfer, actor_user_id=user.id, event_type="APPROVED", from_status=previous, to_status=transfer.status)
    else:
        _post_transfer(db, transfer, user.id)
    db.commit()
    db.refresh(transfer)
    return transfer


def cancel_transfer(db: Session, user: User, transfer_id: int) -> Transfer:
    transfer = get_transfer_with_access(db, user, transfer_id)
    if transfer.status not in CANCELLABLE_STATUSES:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Transfer can no longer be cancelled")
    if transfer.created_by_user_id != user.id:
        _actor_can_approve_transfer(db, user, transfer)
    previous = transfer.status
    transfer.status = TransferStatus.cancelled
    transfer.cancelled_at = datetime.utcnow()
    _record_event(db, transfer, actor_user_id=user.id, event_type="CANCELLED", from_status=previous, to_status=TransferStatus.cancelled)
    from ..ledger.models import HoldStatus
    from ..ledger.service import release_hold_for_transfer

    release_hold_for_transfer(db, transfer.id, status_value=HoldStatus.cancelled)
    from ..approvals.models import ApprovalRequest, ApprovalStatus

    approval = db.scalar(select(ApprovalRequest).where(ApprovalRequest.transfer_id == transfer.id, ApprovalRequest.status == ApprovalStatus.pending))
    if approval:
        approval.status = ApprovalStatus.cancelled
        approval.completed_at = transfer.cancelled_at
    db.commit()
    db.refresh(transfer)
    return transfer


def post_due_scheduled_transfers(db: Session, *, as_of: date | None = None, actor_user_id: int | None = None, limit: int = 100) -> dict:
    processing_date = as_of or date.today()
    transfers = db.scalars(
        select(Transfer)
        .where(
            Transfer.status == TransferStatus.scheduled,
            Transfer.scheduled_for.is_not(None),
            Transfer.scheduled_for <= processing_date,
        )
        .order_by(Transfer.scheduled_for, Transfer.id)
        .limit(limit)
    ).all()
    posted_ids: list[int] = []
    failed: list[dict] = []
    for transfer in transfers:
        previous = transfer.status
        transfer.status = TransferStatus.processing
        _record_event(
            db,
            transfer,
            actor_user_id=actor_user_id,
            event_type="PROCESSING_STARTED",
            from_status=previous,
            to_status=TransferStatus.processing,
            metadata={"as_of": processing_date.isoformat()},
        )
        try:
            _post_transfer(db, transfer, actor_user_id or transfer.created_by_user_id)
            posted_ids.append(transfer.id)
        except HTTPException as exc:
            transfer.status = TransferStatus.failed
            from ..ledger.models import HoldStatus
            from ..ledger.service import release_hold_for_transfer

            release_hold_for_transfer(db, transfer.id, status_value=HoldStatus.released)
            _record_event(
                db,
                transfer,
                actor_user_id=actor_user_id,
                event_type="PROCESSING_FAILED",
                from_status=TransferStatus.processing,
                to_status=TransferStatus.failed,
                metadata={"detail": exc.detail, "status_code": exc.status_code},
            )
            failed.append({"transfer_id": transfer.id, "detail": exc.detail})
        except Exception as exc:
            transfer.status = TransferStatus.failed
            from ..ledger.models import HoldStatus
            from ..ledger.service import release_hold_for_transfer

            release_hold_for_transfer(db, transfer.id, status_value=HoldStatus.released)
            _record_event(
                db,
                transfer,
                actor_user_id=actor_user_id,
                event_type="PROCESSING_FAILED",
                from_status=TransferStatus.processing,
                to_status=TransferStatus.failed,
                metadata={"detail": str(exc)},
            )
            failed.append({"transfer_id": transfer.id, "detail": str(exc)})
    db.commit()
    return {
        "as_of": processing_date.isoformat(),
        "processed": len(transfers),
        "posted": len(posted_ids),
        "failed": len(failed),
        "posted_ids": posted_ids,
        "failures": failed,
    }
