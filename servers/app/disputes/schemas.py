from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from .models import DisputeReason, DisputeStatus


class DisputeCreate(BaseModel):
    transaction_id: int | None = None
    card_authorization_id: int | None = None
    reason: DisputeReason
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    description: str = Field(min_length=8)

    @model_validator(mode="after")
    def validate_source(self):
        if not self.transaction_id and not self.card_authorization_id:
            raise ValueError("transaction_id or card_authorization_id is required")
        return self


class DisputeStatusUpdate(BaseModel):
    status: DisputeStatus
    notes: str | None = None
    assigned_to_user_id: int | None = None


class DisputeEventRead(BaseModel):
    id: int
    dispute_id: int
    actor_user_id: int | None
    event_type: str
    from_status: str | None
    to_status: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeRead(BaseModel):
    id: int
    case_number: str
    user_id: int
    organization_id: int | None
    account_id: int
    transaction_id: int | None
    card_authorization_id: int | None
    reason: DisputeReason
    status: DisputeStatus
    amount: Decimal
    description: str
    provisional_transaction_id: int | None
    assigned_to_user_id: int | None
    opened_at: datetime
    resolved_at: datetime | None
    events: list[DisputeEventRead] = []

    model_config = {"from_attributes": True}
