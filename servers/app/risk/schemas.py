from datetime import datetime

from pydantic import BaseModel, Field

from .models import ComplianceCaseStatus, RiskAlertStatus, RiskAlertType, RiskSeverity


class ComplianceCaseRead(BaseModel):
    id: int
    case_number: str
    alert_id: int
    status: ComplianceCaseStatus
    assigned_to_user_id: int | None
    opened_by_user_id: int | None
    closed_by_user_id: int | None
    disposition: str | None
    notes: str | None
    created_at: datetime
    closed_at: datetime | None

    model_config = {"from_attributes": True}


class RiskAlertRead(BaseModel):
    id: int
    organization_id: int | None
    user_id: int | None
    transfer_id: int | None
    account_id: int | None
    alert_type: RiskAlertType
    severity: RiskSeverity
    status: RiskAlertStatus
    rule_code: str
    title: str
    description: str
    metadata_json: str | None
    assigned_to_user_id: int | None
    resolved_by_user_id: int | None
    resolution_notes: str | None
    created_at: datetime
    resolved_at: datetime | None
    case: ComplianceCaseRead | None = None

    model_config = {"from_attributes": True}


class AssignRiskAlertRequest(BaseModel):
    assigned_to_user_id: int


class ResolveRiskAlertRequest(BaseModel):
    resolution_notes: str = Field(min_length=2, max_length=500)


class ComplianceCaseUpdate(BaseModel):
    status: ComplianceCaseStatus | None = None
    assigned_to_user_id: int | None = None
    disposition: str | None = Field(default=None, max_length=120)
    notes: str | None = None
