import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class RiskAlertType(str, enum.Enum):
    high_value_transfer = "high_value_transfer"
    external_transfer_review = "external_transfer_review"
    new_beneficiary_transfer = "new_beneficiary_transfer"
    kyc_review = "kyc_review"
    high_risk_customer = "high_risk_customer"
    transfer_velocity = "transfer_velocity"


class RiskSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskAlertStatus(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    dismissed = "dismissed"


class ComplianceCaseStatus(str, enum.Enum):
    open = "open"
    in_review = "in_review"
    escalated = "escalated"
    closed = "closed"


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    transfer_id: Mapped[int | None] = mapped_column(ForeignKey("transfers.id"), index=True)
    account_id: Mapped[int | None] = mapped_column(ForeignKey("accounts.id"), index=True)
    alert_type: Mapped[RiskAlertType] = mapped_column(Enum(RiskAlertType), index=True, nullable=False)
    severity: Mapped[RiskSeverity] = mapped_column(Enum(RiskSeverity), index=True, nullable=False)
    status: Mapped[RiskAlertStatus] = mapped_column(Enum(RiskAlertStatus), default=RiskAlertStatus.open, index=True, nullable=False)
    rule_code: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    resolved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    resolution_notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    case = relationship("ComplianceCase", back_populates="alert", uselist=False, cascade="all, delete-orphan")


class ComplianceCase(Base):
    __tablename__ = "compliance_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_number: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    alert_id: Mapped[int] = mapped_column(ForeignKey("risk_alerts.id"), unique=True, index=True, nullable=False)
    status: Mapped[ComplianceCaseStatus] = mapped_column(Enum(ComplianceCaseStatus), default=ComplianceCaseStatus.open, index=True, nullable=False)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    opened_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    closed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    disposition: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    alert = relationship("RiskAlert", back_populates="case")
