from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..audit.service import record_audit
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .models import ComplianceCaseStatus, RiskAlertStatus
from .schemas import AssignRiskAlertRequest, ComplianceCaseRead, ComplianceCaseUpdate, ResolveRiskAlertRequest, RiskAlertRead
from .service import assign_alert, get_alert, list_alerts, list_cases, resolve_alert, update_case


risk_router = APIRouter(prefix="/risk", tags=["risk"])
compliance_router = APIRouter(prefix="/compliance", tags=["compliance"])


@risk_router.get("/alerts", response_model=list[RiskAlertRead])
def alerts(
    status_filter: RiskAlertStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("risk:read")),
):
    return list_alerts(db, user, status_filter)


@risk_router.get("/alerts/{alert_id}", response_model=RiskAlertRead)
def alert(alert_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("risk:read"))):
    return get_alert(db, user, alert_id)


@risk_router.post("/alerts/{alert_id}/assign", response_model=RiskAlertRead)
def assign(
    alert_id: int,
    payload: AssignRiskAlertRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("risk:manage")),
):
    alert = assign_alert(db, user, alert_id, payload.assigned_to_user_id)
    record_audit(db, action="RISK_ALERT_ASSIGNED", actor_user_id=user.id, resource_type="risk_alert", resource_id=alert.id, request=request)
    return alert


@risk_router.post("/alerts/{alert_id}/resolve", response_model=RiskAlertRead)
def resolve(
    alert_id: int,
    payload: ResolveRiskAlertRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("risk:manage")),
):
    alert = resolve_alert(db, user, alert_id, payload.resolution_notes)
    record_audit(db, action="RISK_ALERT_RESOLVED", actor_user_id=user.id, resource_type="risk_alert", resource_id=alert.id, request=request)
    return alert


@risk_router.post("/alerts/{alert_id}/dismiss", response_model=RiskAlertRead)
def dismiss(
    alert_id: int,
    payload: ResolveRiskAlertRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("risk:manage")),
):
    alert = resolve_alert(db, user, alert_id, payload.resolution_notes, dismissed=True)
    record_audit(db, action="RISK_ALERT_DISMISSED", actor_user_id=user.id, resource_type="risk_alert", resource_id=alert.id, request=request)
    return alert


@compliance_router.get("/cases", response_model=list[ComplianceCaseRead])
def cases(
    status_filter: ComplianceCaseStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("compliance:read")),
):
    return list_cases(db, user, status_filter)


@compliance_router.patch("/cases/{case_id}", response_model=ComplianceCaseRead)
def patch_case(
    case_id: int,
    payload: ComplianceCaseUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("compliance:manage")),
):
    case = update_case(db, user, case_id, payload)
    record_audit(db, action="COMPLIANCE_CASE_UPDATED", actor_user_id=user.id, resource_type="compliance_case", resource_id=case.id, request=request)
    return case
