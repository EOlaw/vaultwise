import enum
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class ApprovalTargetType(str, enum.Enum):
    transfer = "transfer"


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class ApprovalDecisionType(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"


class ApprovalPolicy(Base):
    __tablename__ = "approval_policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    transfer_type: Mapped[str | None] = mapped_column(String(40), index=True)
    min_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    required_approvals: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    require_separate_approver: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), index=True)
    target_type: Mapped[ApprovalTargetType] = mapped_column(Enum(ApprovalTargetType), default=ApprovalTargetType.transfer, index=True, nullable=False)
    transfer_id: Mapped[int] = mapped_column(ForeignKey("transfers.id"), unique=True, index=True, nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.pending, index=True, nullable=False)
    required_approvals: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    current_approvals: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    require_separate_approver: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    decisions = relationship("ApprovalDecision", back_populates="approval_request", cascade="all, delete-orphan", order_by="ApprovalDecision.created_at")


class ApprovalDecision(Base):
    __tablename__ = "approval_decisions"
    __table_args__ = (UniqueConstraint("approval_request_id", "actor_user_id", name="uq_approval_decision_actor"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    approval_request_id: Mapped[int] = mapped_column(ForeignKey("approval_requests.id"), index=True, nullable=False)
    actor_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    decision: Mapped[ApprovalDecisionType] = mapped_column(Enum(ApprovalDecisionType), index=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    approval_request = relationship("ApprovalRequest", back_populates="decisions")
