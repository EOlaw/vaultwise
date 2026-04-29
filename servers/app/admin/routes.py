from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..accounts.models import Account
from ..approvals.models import ApprovalRequest
from ..auth.models import IdempotencyKey, MultiFactorDevice
from ..database import get_db
from ..audit.models import AuditLog, SecurityEvent
from ..cards.models import Card, CardAuthorization
from ..dependencies import require_permission
from ..disputes.models import Dispute
from ..ledger.models import AccountHold, LedgerEntry
from ..notifications.models import Notification
from ..organizations.models import AccountEntitlement, Organization, OrganizationMembership
from ..risk.models import ComplianceCase, RiskAlert
from ..statements.models import AccountStatement
from ..transactions.models import Transaction
from ..transfers.models import Beneficiary, Transfer
from ..users.models import User


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/metrics")
def metrics(db: Session = Depends(get_db), _: User = Depends(require_permission("admin:metrics"))):
    return {
        "users": db.scalar(select(func.count(User.id))),
        "accounts": db.scalar(select(func.count(Account.id))),
        "transactions": db.scalar(select(func.count(Transaction.id))),
        "organizations": db.scalar(select(func.count(Organization.id))),
        "memberships": db.scalar(select(func.count(OrganizationMembership.id))),
        "account_entitlements": db.scalar(select(func.count(AccountEntitlement.id))),
        "beneficiaries": db.scalar(select(func.count(Beneficiary.id))),
        "transfers": db.scalar(select(func.count(Transfer.id))),
        "approval_requests": db.scalar(select(func.count(ApprovalRequest.id))),
        "risk_alerts": db.scalar(select(func.count(RiskAlert.id))),
        "compliance_cases": db.scalar(select(func.count(ComplianceCase.id))),
        "ledger_entries": db.scalar(select(func.count(LedgerEntry.id))),
        "account_holds": db.scalar(select(func.count(AccountHold.id))),
        "statements": db.scalar(select(func.count(AccountStatement.id))),
        "notifications": db.scalar(select(func.count(Notification.id))),
        "cards": db.scalar(select(func.count(Card.id))),
        "card_authorizations": db.scalar(select(func.count(CardAuthorization.id))),
        "disputes": db.scalar(select(func.count(Dispute.id))),
        "mfa_devices": db.scalar(select(func.count(MultiFactorDevice.id))),
        "idempotency_keys": db.scalar(select(func.count(IdempotencyKey.id))),
    }


@router.get("/audit-logs")
def audit_logs(db: Session = Depends(get_db), _: User = Depends(require_permission("audit:read"))):
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(200)).all()


@router.get("/security-events")
def security_events(db: Session = Depends(get_db), _: User = Depends(require_permission("audit:read"))):
    return db.scalars(select(SecurityEvent).order_by(SecurityEvent.created_at.desc()).limit(200)).all()
