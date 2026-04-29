from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from ..audit.service import record_audit
from ..auth.idempotency import begin_idempotent_request, finalize_idempotent_request
from ..auth.models import UserSession
from ..database import get_db
from ..dependencies import require_permission, require_step_up
from ..users.models import User
from .models import CardStatus
from .schemas import CardAuthorizationCreate, CardAuthorizationRead, CardControlRead, CardControlUpdate, CardCreate, CardRead
from .service import (
    authorize_card,
    capture_authorization,
    create_card,
    get_authorization_with_access,
    get_card_with_access,
    list_authorizations,
    list_cards,
    reverse_authorization,
    set_card_status,
    update_controls,
)


router = APIRouter(prefix="/cards", tags=["cards"])


@router.get("", response_model=list[CardRead])
def cards(account_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:read"))):
    return list_cards(db, user, account_id)


@router.post("", response_model=CardRead, status_code=status.HTTP_201_CREATED)
def issue_card(
    payload: CardCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cards:issue")),
    _: UserSession = Depends(require_step_up),
):
    card = create_card(db, user, payload)
    record_audit(db, action="CARD_ISSUED", actor_user_id=user.id, resource_type="card", resource_id=card.id, request=request)
    return card


@router.get("/authorizations/list", response_model=list[CardAuthorizationRead])
def authorizations(card_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:read"))):
    return list_authorizations(db, user, card_id)


@router.post("/authorizations", response_model=CardAuthorizationRead, status_code=status.HTTP_201_CREATED)
def authorize(
    payload: CardAuthorizationCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cards:authorize")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, payload)
    if idempotency.replay:
        return get_authorization_with_access(db, user, int(idempotency.record.resource_id))
    authorization = authorize_card(db, user, payload)
    finalize_idempotent_request(db, idempotency, resource_type="card_authorization", resource_id=authorization.id, status_code=status.HTTP_201_CREATED)
    record_audit(db, action="CARD_AUTHORIZATION_CREATED", actor_user_id=user.id, resource_type="card_authorization", resource_id=authorization.id, request=request, metadata={"status": authorization.status.value})
    return authorization


@router.post("/authorizations/{authorization_id}/capture", response_model=CardAuthorizationRead)
def capture(
    authorization_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cards:capture")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"action": "capture", "authorization_id": authorization_id})
    if idempotency.replay:
        return get_authorization_with_access(db, user, int(idempotency.record.resource_id))
    authorization = capture_authorization(db, user, authorization_id)
    finalize_idempotent_request(db, idempotency, resource_type="card_authorization", resource_id=authorization.id)
    record_audit(db, action="CARD_AUTHORIZATION_CAPTURED", actor_user_id=user.id, resource_type="card_authorization", resource_id=authorization.id, request=request)
    return authorization


@router.post("/authorizations/{authorization_id}/reverse", response_model=CardAuthorizationRead)
def reverse(
    authorization_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cards:authorize")),
    _: UserSession = Depends(require_step_up),
):
    idempotency = begin_idempotent_request(db, user, request, {"action": "reverse", "authorization_id": authorization_id})
    if idempotency.replay:
        return get_authorization_with_access(db, user, int(idempotency.record.resource_id))
    authorization = reverse_authorization(db, user, authorization_id)
    finalize_idempotent_request(db, idempotency, resource_type="card_authorization", resource_id=authorization.id)
    record_audit(db, action="CARD_AUTHORIZATION_REVERSED", actor_user_id=user.id, resource_type="card_authorization", resource_id=authorization.id, request=request)
    return authorization


@router.get("/{card_id}", response_model=CardRead)
def card(card_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:read"))):
    return get_card_with_access(db, user, card_id)


@router.patch("/{card_id}/controls", response_model=CardControlRead)
def controls(
    card_id: int,
    payload: CardControlUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_permission("cards:manage")),
    _: UserSession = Depends(require_step_up),
):
    control = update_controls(db, user, card_id, payload)
    record_audit(db, action="CARD_CONTROLS_UPDATED", actor_user_id=user.id, resource_type="card", resource_id=card_id, request=request)
    return control


@router.post("/{card_id}/freeze", response_model=CardRead)
def freeze(card_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:manage")), _: UserSession = Depends(require_step_up)):
    card = set_card_status(db, user, card_id, CardStatus.frozen)
    record_audit(db, action="CARD_FROZEN", actor_user_id=user.id, resource_type="card", resource_id=card.id, request=request)
    return card


@router.post("/{card_id}/turn-off", response_model=CardRead)
def turn_off(card_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:manage")), _: UserSession = Depends(require_step_up)):
    card = set_card_status(db, user, card_id, CardStatus.frozen)
    record_audit(db, action="CARD_TURNED_OFF", actor_user_id=user.id, resource_type="card", resource_id=card.id, request=request)
    return card


@router.post("/{card_id}/unfreeze", response_model=CardRead)
def unfreeze(card_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:manage")), _: UserSession = Depends(require_step_up)):
    card = set_card_status(db, user, card_id, CardStatus.active)
    record_audit(db, action="CARD_UNFROZEN", actor_user_id=user.id, resource_type="card", resource_id=card.id, request=request)
    return card


@router.post("/{card_id}/turn-on", response_model=CardRead)
def turn_on(card_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:manage")), _: UserSession = Depends(require_step_up)):
    card = set_card_status(db, user, card_id, CardStatus.active)
    record_audit(db, action="CARD_TURNED_ON", actor_user_id=user.id, resource_type="card", resource_id=card.id, request=request)
    return card


@router.post("/{card_id}/close", response_model=CardRead)
def close(card_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(require_permission("cards:manage")), _: UserSession = Depends(require_step_up)):
    card = set_card_status(db, user, card_id, CardStatus.closed)
    record_audit(db, action="CARD_CLOSED", actor_user_id=user.id, resource_type="card", resource_id=card.id, request=request)
    return card
