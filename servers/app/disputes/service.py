from datetime import date, datetime
from decimal import Decimal
import secrets

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..accounts.service import account_with_access, accessible_account_ids
from ..cards.models import CardAuthorization, CardAuthorizationStatus
from ..iam.policies import INTERNAL_ROLES
from ..iam.service import user_role_names
from ..ledger.service import record_transaction_ledger_entry
from ..transactions.models import Transaction, TransactionType
from ..users.models import User
from .models import Dispute, DisputeEvent, DisputeStatus
from .schemas import DisputeCreate, DisputeStatusUpdate


DISPUTE_STAFF_ROLES = {"super_admin", "bank_admin", "support_agent", "compliance_officer", "risk_manager"}


def _is_dispute_staff(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & DISPUTE_STAFF_ROLES)


def _case_number() -> str:
    return f"DSP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"


def _record_event(db: Session, dispute: Dispute, *, actor_user_id: int | None, event_type: str, from_status: DisputeStatus | None = None, to_status: DisputeStatus | None = None, notes: str | None = None) -> None:
    db.add(
        DisputeEvent(
            dispute_id=dispute.id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            from_status=from_status.value if from_status else None,
            to_status=to_status.value if to_status else None,
            notes=notes,
        )
    )


def _resolve_source(db: Session, user: User, payload: DisputeCreate) -> tuple[int, int | None, int | None, int | None, Decimal]:
    if payload.card_authorization_id:
        authorization = db.get(CardAuthorization, payload.card_authorization_id)
        if not authorization:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card authorization not found")
        account_with_access(db, user.id, authorization.account_id)
        if authorization.status not in {CardAuthorizationStatus.captured, CardAuthorizationStatus.approved}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only approved or captured card activity can be disputed")
        return authorization.account_id, authorization.organization_id, authorization.transaction_id, authorization.id, Decimal(authorization.amount)
    transaction = db.get(Transaction, int(payload.transaction_id))
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    account = account_with_access(db, user.id, transaction.account_id)
    return transaction.account_id, account.organization_id, transaction.id, None, Decimal(transaction.amount)


def create_dispute(db: Session, user: User, payload: DisputeCreate) -> Dispute:
    account_id, organization_id, transaction_id, card_authorization_id, source_amount = _resolve_source(db, user, payload)
    if payload.amount > source_amount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dispute amount cannot exceed source amount")
    dispute = Dispute(
        case_number=_case_number(),
        user_id=user.id,
        organization_id=organization_id,
        account_id=account_id,
        transaction_id=transaction_id,
        card_authorization_id=card_authorization_id,
        reason=payload.reason,
        status=DisputeStatus.open,
        amount=payload.amount,
        description=payload.description,
    )
    db.add(dispute)
    db.flush()
    _record_event(db, dispute, actor_user_id=user.id, event_type="OPENED", to_status=DisputeStatus.open, notes=payload.description)
    db.commit()
    db.refresh(dispute)
    return dispute


def _dispute_access_query(db: Session, user: User):
    if _is_dispute_staff(db, user.id) or bool(user_role_names(db, user.id) & INTERNAL_ROLES):
        return select(Dispute)
    account_ids = accessible_account_ids(db, user.id)
    clauses = [Dispute.user_id == user.id]
    if account_ids:
        clauses.append(Dispute.account_id.in_(account_ids))
    return select(Dispute).where(or_(*clauses))


def list_disputes(db: Session, user: User, status_filter: DisputeStatus | None = None) -> list[Dispute]:
    query = _dispute_access_query(db, user)
    if status_filter is not None:
        query = query.where(Dispute.status == status_filter)
    return db.scalars(query.order_by(Dispute.opened_at.desc(), Dispute.id.desc())).unique().all()


def get_dispute_with_access(db: Session, user: User, dispute_id: int) -> Dispute:
    dispute = db.scalar(_dispute_access_query(db, user).where(Dispute.id == dispute_id))
    if not dispute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispute not found")
    return dispute


def update_dispute_status(db: Session, user: User, dispute_id: int, payload: DisputeStatusUpdate) -> Dispute:
    if not _is_dispute_staff(db, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Dispute staff access required")
    dispute = get_dispute_with_access(db, user, dispute_id)
    previous = dispute.status
    if previous in {DisputeStatus.won, DisputeStatus.lost, DisputeStatus.closed}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Resolved disputes cannot be changed")
    dispute.status = payload.status
    if payload.assigned_to_user_id is not None:
        dispute.assigned_to_user_id = payload.assigned_to_user_id
    if payload.status == DisputeStatus.provisional_credit and dispute.provisional_transaction_id is None:
        credit = Transaction(
            user_id=dispute.user_id,
            account_id=dispute.account_id,
            type=TransactionType.income,
            amount=dispute.amount,
            occurred_on=date.today(),
            category="Provisional Credit",
            notes=f"Provisional credit for dispute {dispute.case_number}",
        )
        db.add(credit)
        db.flush()
        record_transaction_ledger_entry(db, credit, actor_user_id=user.id)
        dispute.provisional_transaction_id = credit.id
    if payload.status in {DisputeStatus.won, DisputeStatus.lost, DisputeStatus.closed}:
        dispute.resolved_at = datetime.utcnow()
    _record_event(db, dispute, actor_user_id=user.id, event_type="STATUS_CHANGED", from_status=previous, to_status=payload.status, notes=payload.notes)
    db.commit()
    db.refresh(dispute)
    return dispute
