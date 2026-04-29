from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..audit.service import record_audit
from ..auth.idempotency import begin_idempotent_request, finalize_idempotent_request
from ..auth.models import UserSession
from ..database import get_db
from ..dependencies import require_permission, require_step_up
from ..users.models import User
from .models import DisputeStatus
from .schemas import DisputeCreate, DisputeRead, DisputeStatusUpdate
from .service import create_dispute, get_dispute_with_access, list_disputes, update_dispute_status


router = APIRouter(prefix="/disputes", tags=["disputes"])


@router.get("", response_model=list[DisputeRead])
def disputes(
    status_filter: DisputeStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("disputes:read")),
):
    return list_disputes(db, user, status_filter)


@router.post("", response_model=DisputeRead, status_code=status.HTTP_201_CREATED)
def open_dispute(
    payload: DisputeCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("disputes:create")),
):
    dispute = create_dispute(db, user, payload)
    record_audit(db, action="DISPUTE_OPENED", actor_user_id=user.id, resource_type="dispute", resource_id=dispute.id, request=request)
    return dispute


@router.get("/{dispute_id}", response_model=DisputeRead)
def get_dispute(dispute_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("disputes:read"))):
    return get_dispute_with_access(db, user, dispute_id)


@router.patch("/{dispute_id}/status", response_model=DisputeRead)
def patch_status(
    dispute_id: int,
    payload: DisputeStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("disputes:manage")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"dispute_id": dispute_id, "payload": payload.model_dump(mode="json")})
    if idempotency.replay:
        return get_dispute_with_access(db, user, int(idempotency.record.resource_id))
    dispute = update_dispute_status(db, user, dispute_id, payload)
    finalize_idempotent_request(db, idempotency, resource_type="dispute", resource_id=dispute.id)
    record_audit(db, action="DISPUTE_STATUS_UPDATED", actor_user_id=user.id, resource_type="dispute", resource_id=dispute.id, request=request, metadata={"status": dispute.status.value})
    return dispute
