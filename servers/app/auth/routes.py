from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..dependencies import get_current_session, get_current_user, require_step_up
from ..database import get_db
from ..users.schemas import UserCreate
from ..users.models import User
from .models import UserSession
from .schemas import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    MFAConfirmRequest,
    MFADeviceRead,
    MFASetupRequest,
    MFASetupResponse,
    MFAStatus,
    RefreshRequest,
    SessionRead,
    StepUpRequest,
    StepUpResponse,
    TokenPair,
)
from . import service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    return service.register(db, payload, request)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    return service.login(db, payload.email, payload.password, request, payload.mfa_code)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    return service.refresh(db, payload.refresh_token, request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    session_key = None
    if token:
        from .security import decode_token
        session_key = decode_token(token).get("sid")
    service.logout(db, user, session_key=session_key, request=request)
    return None


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.logout(db, user, request=request)
    return None


@router.get("/mfa", response_model=MFAStatus)
def get_mfa_status(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return service.mfa_status(db, user)


@router.post("/mfa/setup", response_model=MFASetupResponse, status_code=status.HTTP_201_CREATED)
def setup_mfa(
    payload: MFASetupRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.setup_mfa(db, user, payload, request)


@router.post("/mfa/{device_id}/confirm", response_model=MFADeviceRead)
def confirm_mfa(
    device_id: int,
    payload: MFAConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.confirm_mfa_setup(db, user, device_id, payload.code, request)


@router.delete("/mfa/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_mfa(
    device_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    _: UserSession = Depends(require_step_up),
):
    service.disable_mfa_device(db, user, device_id, request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/step-up", response_model=StepUpResponse)
def step_up(
    payload: StepUpRequest,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    session: UserSession = Depends(get_current_session),
):
    return service.step_up(db, user, session.session_key, payload, request)


@router.get("/sessions", response_model=list[SessionRead])
def sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.scalars(select(UserSession).where(UserSession.user_id == user.id).order_by(UserSession.created_at.desc())).all()


@router.post("/sessions/current/trust", response_model=SessionRead)
def trust_current_device(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    session: UserSession = Depends(require_step_up),
):
    return service.trust_device(db, user, session.session_key, request)


@router.delete("/sessions/{session_key}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(session_key: str, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    service.logout(db, user, session_key=session_key, request=request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
