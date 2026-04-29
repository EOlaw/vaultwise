from datetime import datetime
from pydantic import BaseModel


class RoleRead(BaseModel):
    id: int
    name: str
    description: str | None = None

    model_config = {"from_attributes": True}


class PermissionRead(BaseModel):
    id: int
    code: str
    description: str | None = None

    model_config = {"from_attributes": True}


class AssignRoleRequest(BaseModel):
    user_id: int
    role_name: str


class PolicyDecisionRead(BaseModel):
    id: int
    user_id: int | None
    permission: str
    resource_type: str | None
    resource_id: str | None
    decision: str
    reason: str
    created_at: datetime

    model_config = {"from_attributes": True}
