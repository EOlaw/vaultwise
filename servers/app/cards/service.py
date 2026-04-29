from datetime import date, datetime
from decimal import Decimal
import secrets

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..accounts.models import Account, AccountType
from ..accounts.service import account_with_access, accessible_account_ids
from ..auth.security import token_hash
from ..ledger.models import HoldStatus
from ..ledger.service import assert_available_funds, create_hold_for_card_authorization, release_hold_for_card_authorization, record_transaction_ledger_entry
from ..transactions.models import Transaction, TransactionType
from ..users.models import User
from .models import Card, CardAuthorization, CardAuthorizationStatus, CardControl, CardStatus, CardTransactionChannel, CardType
from .schemas import CardAuthorizationCreate, CardControlUpdate, CardCreate


CARD_ELIGIBLE_ACCOUNTS = {AccountType.bank, AccountType.credit_card}


def _new_last4(db: Session) -> str:
    for _ in range(12):
        last4 = f"{secrets.randbelow(10000):04d}"
        if not db.scalar(select(Card).where(Card.last4 == last4)):
            return last4
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to issue card number")


def _new_card_token_hash(db: Session) -> str:
    for _ in range(12):
        candidate = token_hash(secrets.token_urlsafe(32))
        if not db.scalar(select(Card).where(Card.card_token_hash == candidate)):
            return candidate
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to issue card token")


def _default_controls_for(card_type: CardType) -> CardControl:
    if card_type == CardType.credit:
        return CardControl(allow_online=True, allow_card_present=True, allow_contactless=True, allow_international=False, allow_atm=False, require_pin=False)
    if card_type == CardType.savings:
        return CardControl(allow_online=False, allow_card_present=True, allow_contactless=False, allow_international=False, allow_atm=True, require_pin=True)
    if card_type == CardType.virtual:
        return CardControl(allow_online=True, allow_card_present=False, allow_contactless=False, allow_international=False, allow_atm=False, require_pin=False)
    return CardControl(allow_online=True, allow_card_present=True, allow_contactless=True, allow_international=False, allow_atm=True, require_pin=False)


def list_cards(db: Session, user: User, account_id: int | None = None) -> list[Card]:
    if account_id is not None:
        account_with_access(db, user.id, account_id)
        account_ids = [account_id]
    else:
        account_ids = accessible_account_ids(db, user.id)
    if not account_ids:
        return []
    return db.scalars(select(Card).where(Card.account_id.in_(account_ids)).order_by(Card.issued_at.desc(), Card.id.desc())).unique().all()


def get_card_with_access(db: Session, user: User, card_id: int, *, require_manage: bool = False) -> Card:
    card = db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    account_with_access(db, user.id, card.account_id, require_approve=require_manage)
    return card


def create_card(db: Session, user: User, payload: CardCreate) -> Card:
    account = account_with_access(db, user.id, payload.account_id, require_approve=True)
    if account.type not in CARD_ELIGIBLE_ACCOUNTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cards can only be issued for bank or credit card accounts")
    if payload.card_type == CardType.credit and account.type != AccountType.credit_card:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credit cards must be issued against a credit card account")
    if payload.card_type in {CardType.debit, CardType.savings, CardType.virtual} and account.type != AccountType.bank:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debit, savings, and virtual cards must be linked to a bank account")
    cardholder_id = payload.user_id or user.id
    card = Card(
        account_id=account.id,
        user_id=cardholder_id,
        organization_id=account.organization_id,
        card_type=payload.card_type,
        network=payload.network,
        status=CardStatus.active,
        display_name=payload.display_name,
        card_token_hash=_new_card_token_hash(db),
        last4=_new_last4(db),
        expiry_month=12,
        expiry_year=date.today().year + 4,
        daily_limit=payload.daily_limit,
        monthly_limit=payload.monthly_limit,
    )
    db.add(card)
    db.flush()
    controls = _default_controls_for(payload.card_type)
    controls.card_id = card.id
    db.add(controls)
    db.commit()
    db.refresh(card)
    return card


def update_controls(db: Session, user: User, card_id: int, payload: CardControlUpdate) -> CardControl:
    card = get_card_with_access(db, user, card_id, require_manage=True)
    control = card.controls or CardControl(card_id=card.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(control, key, value)
    control.updated_at = datetime.utcnow()
    db.add(control)
    db.commit()
    db.refresh(control)
    return control


def set_card_status(db: Session, user: User, card_id: int, target_status: CardStatus) -> Card:
    card = get_card_with_access(db, user, card_id, require_manage=True)
    if card.status == CardStatus.closed and target_status != CardStatus.closed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Closed cards cannot be reactivated")
    card.status = target_status
    if target_status == CardStatus.frozen:
        card.frozen_at = datetime.utcnow()
    elif target_status == CardStatus.active:
        card.frozen_at = None
    elif target_status == CardStatus.closed:
        card.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(card)
    return card


def _approved_amount_for_period(db: Session, card: Card, *, start: datetime) -> Decimal:
    total = db.scalar(
        select(func.coalesce(func.sum(CardAuthorization.amount), 0)).where(
            CardAuthorization.card_id == card.id,
            CardAuthorization.status.in_([CardAuthorizationStatus.approved, CardAuthorizationStatus.captured]),
            CardAuthorization.authorized_at >= start,
        )
    )
    return Decimal(total or 0)


def _decline(db: Session, card: Card, payload: CardAuthorizationCreate, reason: str) -> CardAuthorization:
    auth = CardAuthorization(
        card_id=card.id,
        account_id=card.account_id,
        user_id=card.user_id,
        organization_id=card.organization_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        merchant_name=payload.merchant_name,
        merchant_category=payload.merchant_category,
        merchant_country=payload.merchant_country.upper(),
        card_not_present=payload.card_not_present,
        channel=payload.channel,
        status=CardAuthorizationStatus.declined,
        decline_reason=reason,
    )
    db.add(auth)
    db.commit()
    db.refresh(auth)
    return auth


def authorize_card(db: Session, user: User, payload: CardAuthorizationCreate) -> CardAuthorization:
    card = get_card_with_access(db, user, payload.card_id)
    if card.status != CardStatus.active:
        return _decline(db, card, payload, "Card is not active")
    controls = card.controls or CardControl(card_id=card.id)
    if payload.card_not_present and not controls.allow_online:
        return _decline(db, card, payload, "Online transactions are disabled")
    if payload.channel == CardTransactionChannel.online and not controls.allow_online:
        return _decline(db, card, payload, "Online transactions are disabled")
    if payload.channel == CardTransactionChannel.card_present and not controls.allow_card_present:
        return _decline(db, card, payload, "Card-present transactions are disabled")
    if payload.channel == CardTransactionChannel.contactless and not controls.allow_contactless:
        return _decline(db, card, payload, "Contactless transactions are disabled")
    if payload.channel == CardTransactionChannel.atm and not controls.allow_atm:
        return _decline(db, card, payload, "ATM transactions are disabled")
    if payload.merchant_country.upper() != "US" and not controls.allow_international:
        return _decline(db, card, payload, "International transactions are disabled")
    blocked = {item.strip().lower() for item in (controls.blocked_merchant_categories or "").split(",") if item.strip()}
    if payload.merchant_category.lower() in blocked:
        return _decline(db, card, payload, "Merchant category is blocked")
    if controls.max_transaction_amount is not None and payload.amount > Decimal(controls.max_transaction_amount):
        return _decline(db, card, payload, "Card transaction limit exceeded")

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    month_start = datetime(now.year, now.month, 1)
    if card.daily_limit is not None and _approved_amount_for_period(db, card, start=today_start) + payload.amount > Decimal(card.daily_limit):
        return _decline(db, card, payload, "Daily card limit exceeded")
    if card.monthly_limit is not None and _approved_amount_for_period(db, card, start=month_start) + payload.amount > Decimal(card.monthly_limit):
        return _decline(db, card, payload, "Monthly card limit exceeded")

    account = db.get(Account, card.account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card account not found")
    try:
        assert_available_funds(db, account, payload.amount)
    except HTTPException:
        return _decline(db, card, payload, "Insufficient available balance")

    auth = CardAuthorization(
        card_id=card.id,
        account_id=card.account_id,
        user_id=card.user_id,
        organization_id=card.organization_id,
        amount=payload.amount,
        currency=payload.currency.upper(),
        merchant_name=payload.merchant_name,
        merchant_category=payload.merchant_category,
        merchant_country=payload.merchant_country.upper(),
        card_not_present=payload.card_not_present,
        channel=payload.channel,
        status=CardAuthorizationStatus.approved,
    )
    db.add(auth)
    db.flush()
    create_hold_for_card_authorization(
        db,
        account_id=card.account_id,
        card_authorization_id=auth.id,
        amount=auth.amount,
        currency=auth.currency,
        actor_user_id=user.id,
        reason=f"Card authorization at {auth.merchant_name}",
    )
    db.commit()
    db.refresh(auth)
    return auth


def list_authorizations(db: Session, user: User, card_id: int | None = None) -> list[CardAuthorization]:
    if card_id is not None:
        card = get_card_with_access(db, user, card_id)
        card_ids = [card.id]
    else:
        cards = list_cards(db, user)
        card_ids = [card.id for card in cards]
    if not card_ids:
        return []
    return db.scalars(select(CardAuthorization).where(CardAuthorization.card_id.in_(card_ids)).order_by(CardAuthorization.authorized_at.desc(), CardAuthorization.id.desc())).all()


def get_authorization_with_access(db: Session, user: User, authorization_id: int) -> CardAuthorization:
    auth = db.get(CardAuthorization, authorization_id)
    if not auth:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card authorization not found")
    account_with_access(db, user.id, auth.account_id)
    return auth


def capture_authorization(db: Session, user: User, authorization_id: int) -> CardAuthorization:
    auth = get_authorization_with_access(db, user, authorization_id)
    if auth.status != CardAuthorizationStatus.approved:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved authorizations can be captured")
    transaction = Transaction(
        user_id=auth.user_id,
        account_id=auth.account_id,
        type=TransactionType.expense,
        amount=auth.amount,
        occurred_on=date.today(),
        category=auth.merchant_category,
        notes=f"Card purchase at {auth.merchant_name}",
    )
    db.add(transaction)
    db.flush()
    record_transaction_ledger_entry(db, transaction, actor_user_id=user.id)
    release_hold_for_card_authorization(db, auth.id)
    auth.status = CardAuthorizationStatus.captured
    auth.transaction_id = transaction.id
    auth.captured_at = datetime.utcnow()
    db.commit()
    db.refresh(auth)
    return auth


def reverse_authorization(db: Session, user: User, authorization_id: int) -> CardAuthorization:
    auth = get_authorization_with_access(db, user, authorization_id)
    if auth.status != CardAuthorizationStatus.approved:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only approved authorizations can be reversed")
    release_hold_for_card_authorization(db, auth.id, status_value=HoldStatus.cancelled)
    auth.status = CardAuthorizationStatus.reversed
    auth.reversed_at = datetime.utcnow()
    db.commit()
    db.refresh(auth)
    return auth
