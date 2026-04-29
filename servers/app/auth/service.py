from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from ..audit.service import record_audit, record_security_event, request_ip, request_user_agent
from ..config import get_settings
from ..iam.service import sync_legacy_user_role
from ..users.models import User
from ..users.schemas import UserCreate
from ..users.service import create_user, get_by_email
from .mfa import (
    consume_recovery_code,
    decrypted_secret,
    encrypted_secret,
    generate_recovery_codes,
    generate_totp_secret,
    otpauth_uri,
    recovery_code_hashes,
    verify_totp_code,
)
from .models import LoginAttempt, MultiFactorDevice, RefreshToken, UserSession
from .schemas import MFASetupRequest, MFASetupResponse, StepUpRequest, StepUpResponse, TokenPair
from .security import create_access_token, create_refresh_token, decode_token, new_token_id, token_hash, verify_password


settings = get_settings()
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _record_login_attempt(db: Session, *, email: str, user: User | None, success: bool, request: Request | None, reason: str | None = None) -> None:
    db.add(LoginAttempt(
        email=email.lower(),
        user_id=user.id if user else None,
        success=success,
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
        reason=reason,
    ))
    db.commit()


def _device_fingerprint_hash(request: Request | None) -> str | None:
    if not request:
        return None
    fingerprint = request.headers.get("x-device-fingerprint")
    if not fingerprint:
        return None
    return token_hash(fingerprint.strip())


def _assert_not_locked(db: Session, email: str, request: Request | None) -> None:
    since = _utcnow() - timedelta(minutes=LOCKOUT_MINUTES)
    failures = db.scalar(select(func.count(LoginAttempt.id)).where(
        LoginAttempt.email == email.lower(),
        LoginAttempt.success.is_(False),
        LoginAttempt.created_at >= since,
        LoginAttempt.ip_address == request_ip(request),
    ))
    if failures and failures >= MAX_FAILED_ATTEMPTS:
        record_security_event(db, event_type="LOGIN_LOCKOUT", severity="high", request=request, details={"email": email})
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many failed login attempts. Try again later.")


def _create_session(db: Session, user: User, request: Request | None, *, mfa_authenticated: bool = False) -> UserSession:
    now = _utcnow()
    fingerprint_hash = _device_fingerprint_hash(request)
    trusted_device = False
    if fingerprint_hash:
        trusted_device = bool(
            db.scalar(
                select(UserSession).where(
                    UserSession.user_id == user.id,
                    UserSession.device_fingerprint_hash == fingerprint_hash,
                    UserSession.trusted_device.is_(True),
                )
            )
        )
    session = UserSession(
        user_id=user.id,
        session_key=new_token_id(),
        ip_address=request_ip(request),
        user_agent=request_user_agent(request),
        device_label=request.headers.get("x-device-label")[:120] if request and request.headers.get("x-device-label") else None,
        device_fingerprint_hash=fingerprint_hash,
        trusted_device=trusted_device,
        mfa_authenticated_at=now if mfa_authenticated else None,
        step_up_expires_at=(now + timedelta(minutes=settings.step_up_expire_minutes)) if mfa_authenticated else None,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    if fingerprint_hash and not trusted_device:
        record_security_event(db, event_type="NEW_DEVICE_SESSION", user_id=user.id, severity="medium", request=request, details={"session_id": session.id})
    return session


def _store_refresh_token(db: Session, *, user: User, session: UserSession, parent_token_id: str | None = None) -> tuple[str, str]:
    token_id = new_token_id()
    refresh_token = create_refresh_token(str(user.id), session.session_key, token_id)
    db.add(RefreshToken(
        user_id=user.id,
        session_id=session.id,
        token_id=token_id,
        token_hash=token_hash(refresh_token),
        parent_token_id=parent_token_id,
        expires_at=_utcnow() + timedelta(days=settings.refresh_token_expire_days),
    ))
    db.commit()
    return refresh_token, token_id


def token_pair_for_session(db: Session, user: User, session: UserSession, parent_token_id: str | None = None) -> TokenPair:
    refresh_token, _ = _store_refresh_token(db, user=user, session=session, parent_token_id=parent_token_id)
    return TokenPair(
        access_token=create_access_token(str(user.id), session.session_key),
        refresh_token=refresh_token,
        session_key=session.session_key,
    )


def enabled_mfa_device(db: Session, user_id: int) -> MultiFactorDevice | None:
    return db.scalar(
        select(MultiFactorDevice).where(
            MultiFactorDevice.user_id == user_id,
            MultiFactorDevice.is_active.is_(True),
            MultiFactorDevice.is_confirmed.is_(True),
        )
    )


def verify_mfa_for_user(db: Session, user: User, code: str | None, request: Request | None = None) -> bool:
    if not code:
        return False
    device = enabled_mfa_device(db, user.id)
    if not device:
        return False
    secret = decrypted_secret(device)
    if verify_totp_code(secret, code):
        device.last_used_at = _utcnow()
        db.commit()
        return True
    if consume_recovery_code(device, code):
        device.last_used_at = _utcnow()
        db.commit()
        record_security_event(db, event_type="MFA_RECOVERY_CODE_USED", user_id=user.id, severity="medium", request=request, details={"device_id": device.id})
        return True
    return False


def register(db: Session, payload: UserCreate, request: Request | None = None):
    user = create_user(db, payload)
    sync_legacy_user_role(db, user)
    session = _create_session(db, user, request)
    tokens = token_pair_for_session(db, user, session)
    record_audit(db, action="USER_REGISTERED", actor_user_id=user.id, resource_type="user", resource_id=user.id, request=request)
    record_security_event(db, event_type="USER_REGISTERED", user_id=user.id, request=request)
    return {"user": user, **tokens.model_dump()}


def login(db: Session, email: str, password: str, request: Request | None = None, mfa_code: str | None = None):
    _assert_not_locked(db, email, request)
    user = get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        _record_login_attempt(db, email=email, user=user, success=False, request=request, reason="bad_credentials")
        record_security_event(db, event_type="LOGIN_FAILED", user_id=user.id if user else None, severity="medium", request=request, details={"email": email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        _record_login_attempt(db, email=email, user=user, success=False, request=request, reason="inactive_user")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    sync_legacy_user_role(db, user)
    mfa_required = enabled_mfa_device(db, user.id) is not None
    if mfa_required and not verify_mfa_for_user(db, user, mfa_code, request):
        _record_login_attempt(db, email=email, user=user, success=False, request=request, reason="mfa_failed")
        record_security_event(db, event_type="MFA_LOGIN_FAILED", user_id=user.id, severity="high", request=request, details={"email": email})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="MFA code required")
    _record_login_attempt(db, email=email, user=user, success=True, request=request)
    session = _create_session(db, user, request, mfa_authenticated=mfa_required)
    tokens = token_pair_for_session(db, user, session)
    record_audit(db, action="USER_LOGIN", actor_user_id=user.id, resource_type="session", resource_id=session.id, request=request)
    record_security_event(db, event_type="LOGIN_SUCCESS", user_id=user.id, request=request)
    return {"user": user, **tokens.model_dump()}


def refresh(db: Session, refresh_token: str, request: Request | None = None) -> TokenPair:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    token_id = payload.get("jti")
    session_key = payload.get("sid")
    if not token_id or not session_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    stored = db.scalar(select(RefreshToken).where(RefreshToken.token_id == token_id))
    session = db.scalar(select(UserSession).where(UserSession.session_key == session_key))
    now = _utcnow()
    if not stored or stored.token_hash != token_hash(refresh_token) or not session or not session.is_active:
        record_security_event(db, event_type="REFRESH_REUSE_OR_INVALID", severity="high", request=request, details={"token_id": token_id})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if stored.revoked_at or stored.used_at or stored.expires_at <= now:
        session.is_active = False
        session.revoked_at = now
        db.commit()
        record_security_event(db, event_type="REFRESH_REUSE_DETECTED", user_id=stored.user_id, severity="critical", request=request, details={"token_id": token_id})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired or was already used")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    stored.used_at = now
    session.last_seen_at = now
    db.commit()
    tokens = token_pair_for_session(db, user, session, parent_token_id=token_id)
    record_audit(db, action="REFRESH_TOKEN_ROTATED", actor_user_id=user.id, resource_type="session", resource_id=session.id, request=request)
    return tokens


def logout(db: Session, user: User, session_key: str | None = None, request: Request | None = None) -> None:
    now = _utcnow()
    query = select(UserSession).where(UserSession.user_id == user.id, UserSession.is_active.is_(True))
    if session_key:
        query = query.where(UserSession.session_key == session_key)
    sessions = db.scalars(query).all()
    for session in sessions:
        session.is_active = False
        session.revoked_at = now
        tokens = db.scalars(select(RefreshToken).where(RefreshToken.session_id == session.id, RefreshToken.revoked_at.is_(None))).all()
        for token in tokens:
            token.revoked_at = now
    db.commit()
    record_audit(db, action="SESSION_REVOKED", actor_user_id=user.id, resource_type="session", resource_id=session_key or "all", request=request)


def mfa_status(db: Session, user: User) -> dict:
    devices = db.scalars(
        select(MultiFactorDevice).where(MultiFactorDevice.user_id == user.id, MultiFactorDevice.is_active.is_(True)).order_by(MultiFactorDevice.created_at.desc())
    ).all()
    return {"enabled": any(device.is_confirmed for device in devices), "devices": devices}


def setup_mfa(db: Session, user: User, payload: MFASetupRequest, request: Request | None = None) -> MFASetupResponse:
    secret = generate_totp_secret()
    recovery_codes = generate_recovery_codes()
    device = MultiFactorDevice(
        user_id=user.id,
        device_type="totp",
        label=payload.label,
        secret_encrypted=encrypted_secret(secret),
        recovery_codes_hash=recovery_code_hashes(recovery_codes),
        is_confirmed=False,
        is_active=True,
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    record_security_event(db, event_type="MFA_SETUP_STARTED", user_id=user.id, request=request, details={"device_id": device.id})
    return MFASetupResponse(
        device_id=device.id,
        secret=secret,
        otpauth_url=otpauth_uri(issuer=settings.app_name, email=user.email, secret=secret),
        recovery_codes=recovery_codes,
    )


def confirm_mfa_setup(db: Session, user: User, device_id: int, code: str, request: Request | None = None) -> MultiFactorDevice:
    device = db.get(MultiFactorDevice, device_id)
    if not device or device.user_id != user.id or not device.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MFA device not found")
    if not verify_totp_code(decrypted_secret(device), code):
        record_security_event(db, event_type="MFA_SETUP_CONFIRM_FAILED", user_id=user.id, severity="medium", request=request, details={"device_id": device.id})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
    device.is_confirmed = True
    device.confirmed_at = _utcnow()
    device.last_used_at = device.confirmed_at
    db.commit()
    db.refresh(device)
    record_audit(db, action="MFA_ENABLED", actor_user_id=user.id, resource_type="mfa_device", resource_id=device.id, request=request)
    record_security_event(db, event_type="MFA_ENABLED", user_id=user.id, request=request, details={"device_id": device.id})
    return device


def disable_mfa_device(db: Session, user: User, device_id: int, request: Request | None = None) -> None:
    device = db.get(MultiFactorDevice, device_id)
    if not device or device.user_id != user.id or not device.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MFA device not found")
    device.is_active = False
    db.commit()
    record_audit(db, action="MFA_DISABLED", actor_user_id=user.id, resource_type="mfa_device", resource_id=device.id, request=request)
    record_security_event(db, event_type="MFA_DISABLED", user_id=user.id, severity="medium", request=request, details={"device_id": device.id})


def step_up(db: Session, user: User, session_key: str, payload: StepUpRequest, request: Request | None = None) -> StepUpResponse:
    session = db.scalar(select(UserSession).where(UserSession.user_id == user.id, UserSession.session_key == session_key, UserSession.is_active.is_(True)))
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is inactive")
    mfa_enabled = enabled_mfa_device(db, user.id) is not None
    if mfa_enabled:
        if not verify_mfa_for_user(db, user, payload.mfa_code, request):
            record_security_event(db, event_type="STEP_UP_MFA_FAILED", user_id=user.id, severity="high", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid MFA code required")
        session.mfa_authenticated_at = _utcnow()
    else:
        if not payload.password or not verify_password(payload.password, user.hashed_password):
            record_security_event(db, event_type="STEP_UP_PASSWORD_FAILED", user_id=user.id, severity="medium", request=request)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Valid password required")
    session.step_up_expires_at = _utcnow() + timedelta(minutes=settings.step_up_expire_minutes)
    session.last_seen_at = _utcnow()
    db.commit()
    db.refresh(session)
    record_audit(db, action="SESSION_STEP_UP", actor_user_id=user.id, resource_type="session", resource_id=session.id, request=request)
    record_security_event(db, event_type="STEP_UP_SUCCESS", user_id=user.id, request=request, details={"session_id": session.id, "mfa": mfa_enabled})
    return StepUpResponse(session_key=session.session_key, step_up_expires_at=session.step_up_expires_at)


def trust_device(db: Session, user: User, session_key: str, request: Request | None = None) -> UserSession:
    session = db.scalar(select(UserSession).where(UserSession.user_id == user.id, UserSession.session_key == session_key, UserSession.is_active.is_(True)))
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is inactive")
    if not session.device_fingerprint_hash:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device fingerprint header is required before this device can be trusted")
    session.trusted_device = True
    db.commit()
    db.refresh(session)
    record_audit(db, action="DEVICE_TRUSTED", actor_user_id=user.id, resource_type="session", resource_id=session.id, request=request)
    record_security_event(db, event_type="DEVICE_TRUSTED", user_id=user.id, request=request, details={"session_id": session.id})
    return session
