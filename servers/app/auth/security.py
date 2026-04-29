import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import get_settings


settings = get_settings()
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def new_token_id() -> str:
    return secrets.token_urlsafe(32)


def create_token(subject: str, token_type: str, expires_delta: timedelta, extra_claims: dict | None = None) -> str:
    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "type": token_type, "exp": expires_at}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, session_key: str | None = None) -> str:
    claims = {"sid": session_key} if session_key else None
    return create_token(
        subject,
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
        claims,
    )


def create_refresh_token(subject: str, session_key: str, token_id: str) -> str:
    return create_token(
        subject,
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
        {"sid": session_key, "jti": token_id},
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
