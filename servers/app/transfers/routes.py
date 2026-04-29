from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..audit.service import record_audit
from ..auth.idempotency import begin_idempotent_request, finalize_idempotent_request
from ..auth.models import UserSession
from ..database import get_db
from ..dependencies import require_permission, require_step_up
from ..users.models import User
from .models import TransferStatus
from .schemas import BeneficiaryCreate, BeneficiaryRead, BeneficiaryUpdate, TransferCreate, TransferRead
from .service import (
    approve_transfer,
    cancel_transfer,
    create_beneficiary,
    create_transfer,
    get_transfer_with_access,
    list_beneficiaries,
    list_transfers,
    submit_transfer,
    update_beneficiary,
)


beneficiaries_router = APIRouter(prefix="/beneficiaries", tags=["beneficiaries"])
transfers_router = APIRouter(prefix="/transfers", tags=["transfers"])


@beneficiaries_router.get("", response_model=list[BeneficiaryRead])
def get_beneficiaries(
    organization_id: int | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("beneficiaries:read")),
):
    return list_beneficiaries(db, user, organization_id)


@beneficiaries_router.post("", response_model=BeneficiaryRead, status_code=status.HTTP_201_CREATED)
def create_payee(
    payload: BeneficiaryCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("beneficiaries:create")),
    _: UserSession = Depends(require_step_up),
):
    beneficiary = create_beneficiary(db, user, payload)
    record_audit(
        db,
        action="BENEFICIARY_CREATED",
        actor_user_id=user.id,
        resource_type="beneficiary",
        resource_id=beneficiary.id,
        request=request,
        metadata={"organization_id": beneficiary.organization_id, "beneficiary_type": beneficiary.beneficiary_type.value},
    )
    return beneficiary


@beneficiaries_router.patch("/{beneficiary_id}", response_model=BeneficiaryRead)
def patch_payee(
    beneficiary_id: int,
    payload: BeneficiaryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("beneficiaries:update")),
    _: UserSession = Depends(require_step_up),
):
    beneficiary = update_beneficiary(db, user, beneficiary_id, payload)
    record_audit(
        db,
        action="BENEFICIARY_UPDATED",
        actor_user_id=user.id,
        resource_type="beneficiary",
        resource_id=beneficiary.id,
        request=request,
        metadata={"status": beneficiary.status.value},
    )
    return beneficiary


@transfers_router.get("", response_model=list[TransferRead])
def get_transfers(
    status_filter: TransferStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("transfers:read")),
):
    return list_transfers(db, user, status_filter)


@transfers_router.post("", response_model=TransferRead, status_code=status.HTTP_201_CREATED)
def create_money_movement(
    payload: TransferCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("transfers:create")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, payload)
    if idempotency.replay:
        return get_transfer_with_access(db, user, int(idempotency.record.resource_id))
    transfer = create_transfer(db, user, payload)
    finalize_idempotent_request(db, idempotency, resource_type="transfer", resource_id=transfer.id, status_code=status.HTTP_201_CREATED)
    record_audit(
        db,
        action="TRANSFER_CREATED",
        actor_user_id=user.id,
        resource_type="transfer",
        resource_id=transfer.id,
        request=request,
        metadata={"amount": str(transfer.amount), "transfer_type": transfer.transfer_type.value, "organization_id": transfer.organization_id},
    )
    return transfer


@transfers_router.get("/{transfer_id}", response_model=TransferRead)
def get_transfer(transfer_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("transfers:read"))):
    return get_transfer_with_access(db, user, transfer_id)


@transfers_router.post("/{transfer_id}/submit", response_model=TransferRead)
def submit(
    transfer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("transfers:submit")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"action": "submit", "transfer_id": transfer_id})
    if idempotency.replay:
        return get_transfer_with_access(db, user, int(idempotency.record.resource_id))
    transfer = submit_transfer(db, user, transfer_id)
    finalize_idempotent_request(db, idempotency, resource_type="transfer", resource_id=transfer.id)
    record_audit(db, action="TRANSFER_SUBMITTED", actor_user_id=user.id, resource_type="transfer", resource_id=transfer.id, request=request, metadata={"status": transfer.status.value})
    return transfer


@transfers_router.post("/{transfer_id}/approve", response_model=TransferRead)
def approve(
    transfer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("transfers:approve")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"action": "approve", "transfer_id": transfer_id})
    if idempotency.replay:
        return get_transfer_with_access(db, user, int(idempotency.record.resource_id))
    transfer = approve_transfer(db, user, transfer_id)
    finalize_idempotent_request(db, idempotency, resource_type="transfer", resource_id=transfer.id)
    record_audit(db, action="TRANSFER_APPROVED", actor_user_id=user.id, resource_type="transfer", resource_id=transfer.id, request=request, metadata={"status": transfer.status.value})
    return transfer


@transfers_router.post("/{transfer_id}/cancel", response_model=TransferRead)
def cancel(
    transfer_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("transfers:cancel")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"action": "cancel", "transfer_id": transfer_id})
    if idempotency.replay:
        return get_transfer_with_access(db, user, int(idempotency.record.resource_id))
    transfer = cancel_transfer(db, user, transfer_id)
    finalize_idempotent_request(db, idempotency, resource_type="transfer", resource_id=transfer.id)
    record_audit(db, action="TRANSFER_CANCELLED", actor_user_id=user.id, resource_type="transfer", resource_id=transfer.id, request=request)
    return transfer
