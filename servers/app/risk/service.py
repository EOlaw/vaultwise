import json
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..iam.policies import INTERNAL_ROLES
from ..iam.service import user_role_names
from ..transfers.models import Beneficiary, Transfer, TransferType
from ..users.models import KycStatus, RiskRating, User
from .models import ComplianceCase, ComplianceCaseStatus, RiskAlert, RiskAlertStatus, RiskAlertType, RiskSeverity
from .schemas import ComplianceCaseUpdate


RISK_STAFF_ROLES = {"super_admin", "bank_admin", "compliance_officer", "risk_manager"}
BLOCKING_SEVERITIES = {RiskSeverity.high, RiskSeverity.critical}


def _is_risk_staff(db: Session, user_id: int) -> bool:
    return bool(user_role_names(db, user_id) & RISK_STAFF_ROLES)


def _ensure_risk_staff(db: Session, user: User) -> None:
    if not _is_risk_staff(db, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Risk staff access required")


def _case_number(alert_id: int) -> str:
    return f"CASE-{datetime.utcnow().strftime('%Y%m%d')}-{alert_id:06d}"


def _ensure_case_for_alert(db: Session, alert: RiskAlert, opened_by_user_id: int | None = None) -> ComplianceCase:
    existing = db.scalar(select(ComplianceCase).where(ComplianceCase.alert_id == alert.id))
    if existing:
        return existing
    case = ComplianceCase(
        case_number=_case_number(alert.id),
        alert_id=alert.id,
        status=ComplianceCaseStatus.open,
        opened_by_user_id=opened_by_user_id,
        notes=f"Auto-opened from {alert.rule_code}",
    )
    db.add(case)
    return case


def _create_alert(
    db: Session,
    transfer: Transfer,
    *,
    rule_code: str,
    alert_type: RiskAlertType,
    severity: RiskSeverity,
    title: str,
    description: str,
    metadata: dict | None = None,
) -> RiskAlert:
    existing = db.scalar(select(RiskAlert).where(RiskAlert.transfer_id == transfer.id, RiskAlert.rule_code == rule_code))
    if existing:
        return existing
    alert = RiskAlert(
        organization_id=transfer.organization_id,
        user_id=transfer.created_by_user_id,
        transfer_id=transfer.id,
        account_id=transfer.from_account_id,
        alert_type=alert_type,
        severity=severity,
        status=RiskAlertStatus.open,
        rule_code=rule_code,
        title=title,
        description=description,
        metadata_json=json.dumps(metadata or {}, sort_keys=True),
    )
    db.add(alert)
    db.flush()
    from ..notifications.service import notify_risk_alert_created

    notify_risk_alert_created(db, alert_id=alert.id, title=alert.title, severity=alert.severity.value, organization_id=alert.organization_id)
    if severity in BLOCKING_SEVERITIES:
        _ensure_case_for_alert(db, alert)
    return alert


def screen_transfer(db: Session, transfer: Transfer, actor: User) -> list[RiskAlert]:
    alerts: list[RiskAlert] = []
    amount = Decimal(transfer.amount)
    profile = actor.profile
    if amount >= Decimal("5000.00"):
        alerts.append(
            _create_alert(
                db,
                transfer,
                rule_code="HIGH_VALUE_TRANSFER",
                alert_type=RiskAlertType.high_value_transfer,
                severity=RiskSeverity.high,
                title="High value transfer",
                description="Transfer amount meets high-value review threshold.",
                metadata={"amount": str(amount), "threshold": "5000.00"},
            )
        )
    if transfer.transfer_type != TransferType.internal and amount >= Decimal("1000.00"):
        alerts.append(
            _create_alert(
                db,
                transfer,
                rule_code="EXTERNAL_TRANSFER_REVIEW",
                alert_type=RiskAlertType.external_transfer_review,
                severity=RiskSeverity.medium,
                title="External transfer review",
                description="External money movement exceeds review threshold.",
                metadata={"amount": str(amount), "transfer_type": transfer.transfer_type.value},
            )
        )
    if not profile or profile.kyc_status != KycStatus.verified:
        alerts.append(
            _create_alert(
                db,
                transfer,
                rule_code="KYC_NOT_VERIFIED",
                alert_type=RiskAlertType.kyc_review,
                severity=RiskSeverity.high,
                title="KYC verification required",
                description="Transfer creator does not have verified KYC status.",
                metadata={"user_id": transfer.created_by_user_id},
            )
        )
    if profile and profile.risk_rating == RiskRating.high:
        alerts.append(
            _create_alert(
                db,
                transfer,
                rule_code="HIGH_RISK_CUSTOMER",
                alert_type=RiskAlertType.high_risk_customer,
                severity=RiskSeverity.high,
                title="High risk customer activity",
                description="Transfer was initiated by a high-risk customer profile.",
                metadata={"user_id": transfer.created_by_user_id},
            )
        )
    today_count = int(
        db.scalar(
            select(func.count(Transfer.id)).where(
                Transfer.from_account_id == transfer.from_account_id,
                Transfer.requested_on == transfer.requested_on,
                Transfer.id != transfer.id,
            )
        )
        or 0
    )
    if today_count >= 3:
        alerts.append(
            _create_alert(
                db,
                transfer,
                rule_code="TRANSFER_VELOCITY",
                alert_type=RiskAlertType.transfer_velocity,
                severity=RiskSeverity.medium,
                title="Transfer velocity review",
                description="Multiple transfers were initiated from the same funding account today.",
                metadata={"same_day_transfer_count": today_count + 1},
            )
        )
    if transfer.beneficiary_id:
        beneficiary = db.get(Beneficiary, transfer.beneficiary_id)
        if beneficiary and beneficiary.created_at and beneficiary.created_at >= datetime.utcnow() - timedelta(days=1):
            alerts.append(
                _create_alert(
                    db,
                    transfer,
                    rule_code="NEW_BENEFICIARY_TRANSFER",
                    alert_type=RiskAlertType.new_beneficiary_transfer,
                    severity=RiskSeverity.medium,
                    title="New beneficiary transfer",
                    description="Transfer targets a recently created beneficiary.",
                    metadata={"beneficiary_id": beneficiary.id},
                )
            )
    return alerts


def alerts_require_approval(alerts: list[RiskAlert]) -> bool:
    return any(alert.severity in BLOCKING_SEVERITIES and alert.status in {RiskAlertStatus.open, RiskAlertStatus.in_review} for alert in alerts)


def list_alerts(db: Session, user: User, status_filter: RiskAlertStatus | None = None) -> list[RiskAlert]:
    _ensure_risk_staff(db, user)
    query = select(RiskAlert)
    if status_filter is not None:
        query = query.where(RiskAlert.status == status_filter)
    return db.scalars(query.order_by(RiskAlert.created_at.desc(), RiskAlert.id.desc())).unique().all()


def get_alert(db: Session, user: User, alert_id: int) -> RiskAlert:
    _ensure_risk_staff(db, user)
    alert = db.get(RiskAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risk alert not found")
    return alert


def assign_alert(db: Session, user: User, alert_id: int, assigned_to_user_id: int) -> RiskAlert:
    alert = get_alert(db, user, alert_id)
    if not db.get(User, assigned_to_user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assigned user not found")
    alert.assigned_to_user_id = assigned_to_user_id
    alert.status = RiskAlertStatus.in_review
    if alert.case:
        alert.case.assigned_to_user_id = assigned_to_user_id
        alert.case.status = ComplianceCaseStatus.in_review
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: Session, user: User, alert_id: int, notes: str, *, dismissed: bool = False) -> RiskAlert:
    alert = get_alert(db, user, alert_id)
    alert.status = RiskAlertStatus.dismissed if dismissed else RiskAlertStatus.resolved
    alert.resolved_by_user_id = user.id
    alert.resolution_notes = notes
    alert.resolved_at = datetime.utcnow()
    if alert.case:
        alert.case.status = ComplianceCaseStatus.closed
        alert.case.closed_by_user_id = user.id
        alert.case.closed_at = alert.resolved_at
        alert.case.disposition = "dismissed" if dismissed else "resolved"
        alert.case.notes = notes
    db.commit()
    db.refresh(alert)
    return alert


def list_cases(db: Session, user: User, status_filter: ComplianceCaseStatus | None = None) -> list[ComplianceCase]:
    _ensure_risk_staff(db, user)
    query = select(ComplianceCase)
    if status_filter is not None:
        query = query.where(ComplianceCase.status == status_filter)
    return db.scalars(query.order_by(ComplianceCase.created_at.desc(), ComplianceCase.id.desc())).all()


def update_case(db: Session, user: User, case_id: int, payload: ComplianceCaseUpdate) -> ComplianceCase:
    _ensure_risk_staff(db, user)
    case = db.get(ComplianceCase, case_id)
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compliance case not found")
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(case, key, value)
    if updates.get("status") == ComplianceCaseStatus.closed:
        case.closed_by_user_id = user.id
        case.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case
