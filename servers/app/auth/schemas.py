from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from ..users.schemas import UserRead


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    mfa_code: str | None = Field(default=None, min_length=6, max_length=32)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    session_key: str | None = None
    token_type: str = "bearer"


class AuthResponse(TokenPair):
    user: UserRead


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class MFASetupRequest(BaseModel):
    label: str = Field(default="Authenticator app", min_length=2, max_length=120)


class MFASetupResponse(BaseModel):
    device_id: int
    secret: str
    otpauth_url: str
    recovery_codes: list[str]


class MFAConfirmRequest(BaseModel):
    code: str = Field(min_length=6, max_length=32)


class MFADeviceRead(BaseModel):
    id: int
    device_type: str
    label: str
    is_confirmed: bool
    is_active: bool
    created_at: datetime
    confirmed_at: datetime | None
    last_used_at: datetime | None

    model_config = {"from_attributes": True}


class MFAStatus(BaseModel):
    enabled: bool
    devices: list[MFADeviceRead]


class StepUpRequest(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=128)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=32)


class StepUpResponse(BaseModel):
    session_key: str
    step_up_expires_at: datetime


class SessionRead(BaseModel):
    id: int
    session_key: str
    ip_address: str | None
    user_agent: str | None
    device_label: str | None
    trusted_device: bool
    mfa_authenticated_at: datetime | None
    step_up_expires_at: datetime | None
    is_active: bool
    created_at: datetime
    last_seen_at: datetime

    model_config = {"from_attributes": True}
