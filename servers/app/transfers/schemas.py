from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from .models import BeneficiaryStatus, BeneficiaryType, TransferStatus, TransferType


class BeneficiaryBase(BaseModel):
    organization_id: int | None = None
    beneficiary_type: BeneficiaryType
    display_name: str = Field(min_length=2, max_length=160)
    bank_name: str | None = Field(default=None, max_length=160)
    routing_number_last4: str | None = Field(default=None, min_length=4, max_length=4)
    account_number_last4: str | None = Field(default=None, min_length=4, max_length=4)
    internal_account_id: int | None = None


class BeneficiaryCreate(BeneficiaryBase):
    @model_validator(mode="after")
    def validate_destination(self):
        if self.beneficiary_type == BeneficiaryType.internal_account and self.internal_account_id is None:
            raise ValueError("internal_account_id is required for internal account beneficiaries")
        if self.beneficiary_type != BeneficiaryType.internal_account and not self.account_number_last4:
            raise ValueError("account_number_last4 is required for external beneficiaries")
        return self


class BeneficiaryUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=160)
    bank_name: str | None = Field(default=None, max_length=160)
    status: BeneficiaryStatus | None = None


class BeneficiaryRead(BeneficiaryBase):
    id: int
    owner_user_id: int
    status: BeneficiaryStatus
    created_by_user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TransferCreate(BaseModel):
    organization_id: int | None = None
    from_account_id: int
    to_account_id: int | None = None
    beneficiary_id: int | None = None
    transfer_type: TransferType
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    memo: str | None = Field(default=None, max_length=255)
    scheduled_for: date | None = None

    @model_validator(mode="after")
    def validate_destination(self):
        if self.transfer_type == TransferType.internal and self.to_account_id is None:
            raise ValueError("to_account_id is required for internal transfers")
        if self.transfer_type != TransferType.internal and self.beneficiary_id is None:
            raise ValueError("beneficiary_id is required for external transfers")
        return self


class TransferEventRead(BaseModel):
    id: int
    transfer_id: int
    actor_user_id: int | None
    event_type: str
    from_status: str | None
    to_status: str | None
    metadata_json: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TransferRead(BaseModel):
    id: int
    organization_id: int | None
    created_by_user_id: int
    from_account_id: int
    to_account_id: int | None
    beneficiary_id: int | None
    transfer_type: TransferType
    status: TransferStatus
    amount: Decimal
    currency: str
    memo: str | None
    requested_on: date
    scheduled_for: date | None
    posted_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    events: list[TransferEventRead] = []

    model_config = {"from_attributes": True}
