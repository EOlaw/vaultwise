from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .models import CardAuthorizationStatus, CardNetwork, CardStatus, CardTransactionChannel, CardType


class CardControlRead(BaseModel):
    id: int
    card_id: int
    allow_online: bool
    allow_card_present: bool
    allow_contactless: bool
    allow_international: bool
    allow_atm: bool
    require_pin: bool
    max_transaction_amount: Decimal | None
    blocked_merchant_categories: str | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class CardControlUpdate(BaseModel):
    allow_online: bool | None = None
    allow_card_present: bool | None = None
    allow_contactless: bool | None = None
    allow_international: bool | None = None
    allow_atm: bool | None = None
    require_pin: bool | None = None
    max_transaction_amount: Decimal | None = Field(default=None, ge=0)
    blocked_merchant_categories: str | None = Field(default=None, max_length=500)


class CardCreate(BaseModel):
    account_id: int
    user_id: int | None = None
    card_type: CardType = CardType.debit
    network: CardNetwork = CardNetwork.visa
    display_name: str = Field(min_length=2, max_length=120)
    daily_limit: Decimal | None = Field(default=None, ge=0)
    monthly_limit: Decimal | None = Field(default=None, ge=0)


class CardRead(BaseModel):
    id: int
    account_id: int
    user_id: int
    organization_id: int | None
    card_type: CardType
    network: CardNetwork
    status: CardStatus
    display_name: str
    last4: str
    expiry_month: int
    expiry_year: int
    daily_limit: Decimal | None
    monthly_limit: Decimal | None
    issued_at: datetime
    frozen_at: datetime | None
    closed_at: datetime | None
    controls: CardControlRead | None = None

    model_config = {"from_attributes": True}


class CardAuthorizationCreate(BaseModel):
    card_id: int
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    merchant_name: str = Field(min_length=2, max_length=160)
    merchant_category: str = Field(min_length=2, max_length=80)
    merchant_country: str = Field(default="US", min_length=2, max_length=2)
    card_not_present: bool = False
    channel: CardTransactionChannel = CardTransactionChannel.online


class CardAuthorizationRead(BaseModel):
    id: int
    card_id: int
    account_id: int
    user_id: int
    organization_id: int | None
    transaction_id: int | None
    amount: Decimal
    currency: str
    merchant_name: str
    merchant_category: str
    merchant_country: str
    card_not_present: bool
    channel: CardTransactionChannel
    status: CardAuthorizationStatus
    decline_reason: str | None
    authorized_at: datetime
    captured_at: datetime | None
    reversed_at: datetime | None

    model_config = {"from_attributes": True}
