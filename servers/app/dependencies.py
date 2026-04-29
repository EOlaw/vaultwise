from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .auth.security import decode_token
from .auth.models import UserSession
from .iam.policies import assert_permission
from .users.models import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _access_payload(token: str) -> dict:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    return payload


def get_current_session(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> UserSession:
    payload = _access_payload(token)
    session_key = payload.get("sid")
    if not session_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session claim is required")
    session = db.query(UserSession).filter(UserSession.session_key == session_key, UserSession.is_active.is_(True)).first()
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is inactive")
    session.last_seen_at = _utcnow()
    db.commit()
    db.refresh(session)
    return session


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = _access_payload(token)
    session_key = payload.get("sid")
    if session_key:
        session = db.query(UserSession).filter(UserSession.session_key == session_key, UserSession.is_active.is_(True)).first()
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is inactive")
    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive or missing user")
    return user


def require_step_up(session: UserSession = Depends(get_current_session)) -> UserSession:
    if not session.step_up_expires_at or session.step_up_expires_at <= _utcnow():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Recent step-up authentication required")
    return session


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


def require_permission(permission: str):
    def dependency(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
        assert_permission(db, user, permission)
        return user

    return dependency
