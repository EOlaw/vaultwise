import json
from fastapi import Request
from sqlalchemy.orm import Session
from .models import AuditLog, SecurityEvent


def request_ip(request: Request | None) -> str | None:
    if not request:
        return None
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def request_user_agent(request: Request | None) -> str | None:
    return request.headers.get("user-agent") if request else None


def record_audit(
    db: Session,
    *,
    action: str,
    actor_user_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    outcome: str = "success",
    request: Request | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    entry = AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        outcome=outcome,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
        metadata_json=json.dumps(metadata or {}, sort_keys=True),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


def record_security_event(
    db: Session,
    *,
    event_type: str,
    user_id: int | None = None,
    severity: str = "info",
    request: Request | None = None,
    details: dict | None = None,
) -> SecurityEvent:
    entry = SecurityEvent(
        user_id=user_id,
        event_type=event_type,
        severity=severity,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
        details_json=json.dumps(details or {}, sort_keys=True),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
