from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from .models import ApprovalDecisionType, ApprovalStatus, ApprovalTargetType


class ApprovalPolicyCreate(BaseModel):
    organization_id: int | None = None
    name: str = Field(min_length=2, max_length=160)
    transfer_type: str | None = Field(default=None, max_length=40)
    min_amount: Decimal = Field(default=Decimal("0"), ge=0)
    required_approvals: int = Field(default=1, ge=1, le=4)
    require_separate_approver: bool = True


class ApprovalPolicyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    transfer_type: str | None = Field(default=None, max_length=40)
    min_amount: Decimal | None = Field(default=None, ge=0)
    required_approvals: int | None = Field(default=None, ge=1, le=4)
    require_separate_approver: bool | None = None
    is_active: bool | None = None


class ApprovalPolicyRead(BaseModel):
    id: int
    organization_id: int | None
    name: str
    transfer_type: str | None
    min_amount: Decimal
    required_approvals: int
    require_separate_approver: bool
    is_active: bool
    created_by_user_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalDecisionRead(BaseModel):
    id: int
    approval_request_id: int
    actor_user_id: int
    decision: ApprovalDecisionType
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalRequestRead(BaseModel):
    id: int
    organization_id: int | None
    target_type: ApprovalTargetType
    transfer_id: int
    requested_by_user_id: int
    status: ApprovalStatus
    required_approvals: int
    current_approvals: int
    require_separate_approver: bool
    reason: str
    metadata_json: str | None
    created_at: datetime
    completed_at: datetime | None
    decisions: list[ApprovalDecisionRead] = []

    model_config = {"from_attributes": True}


class ApprovalDecisionRequest(BaseModel):
    notes: str | None = Field(default=None, max_length=500)
