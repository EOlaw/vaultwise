import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import get_settings
from ..users.models import User
from .models import IdempotencyKey
from .security import token_hash


@dataclass
class IdempotencyState:
    record: IdempotencyKey | None
    replay: bool = False


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _payload_json(payload: Any) -> str:
    if hasattr(payload, "model_dump"):
        payload = payload.model_dump(mode="json")
    return json.dumps(payload or {}, sort_keys=True, separators=(",", ":"), default=str)


def _request_hash(request: Request, payload: Any) -> str:
    fingerprint = f"{request.method.upper()}:{request.url.path}:{_payload_json(payload)}"
    return hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()


def begin_idempotent_request(db: Session, user: User, request: Request, payload: Any = None) -> IdempotencyState:
    key = request.headers.get("idempotency-key")
    if not key:
        return IdempotencyState(record=None)
    key = key.strip()
    if len(key) < 8 or len(key) > 128:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Idempotency-Key must be 8 to 128 characters")
    now = _utcnow()
    key_hash = token_hash(f"{user.id}:{key}")
    request_hash = _request_hash(request, payload)
    record = db.scalar(select(IdempotencyKey).where(IdempotencyKey.user_id == user.id, IdempotencyKey.key_hash == key_hash))
    if record and record.expires_at <= now:
        db.delete(record)
        db.commit()
        record = None
    if record:
        if record.request_hash != request_hash or record.method != request.method.upper() or record.path != request.url.path:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotency-Key was already used for a different request")
        if not record.resource_type or not record.resource_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Idempotent request is still processing")
        return IdempotencyState(record=record, replay=True)
    record = IdempotencyKey(
        user_id=user.id,
        key_hash=key_hash,
        request_hash=request_hash,
        method=request.method.upper(),
        path=request.url.path,
        expires_at=now + timedelta(hours=get_settings().idempotency_key_expire_hours),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return IdempotencyState(record=record)


def finalize_idempotent_request(
    db: Session,
    state: IdempotencyState,
    *,
    resource_type: str,
    resource_id: int | str,
    status_code: int = 200,
) -> None:
    if not state.record:
        return
    state.record.resource_type = resource_type
    state.record.resource_id = str(resource_id)
    state.record.status_code = status_code
    db.commit()
