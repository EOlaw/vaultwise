"""approval workflow and risk controls

Revision ID: 20260428_0002
Revises: 20260428_0001
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0002"
down_revision = "20260428_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_policies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("transfer_type", sa.String(length=40), nullable=True),
        sa.Column("min_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("required_approvals", sa.Integer(), nullable=False),
        sa.Column("require_separate_approver", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
    )
    op.create_index(op.f("ix_approval_policies_created_by_user_id"), "approval_policies", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_approval_policies_is_active"), "approval_policies", ["is_active"], unique=False)
    op.create_index(op.f("ix_approval_policies_organization_id"), "approval_policies", ["organization_id"], unique=False)
    op.create_index(op.f("ix_approval_policies_transfer_type"), "approval_policies", ["transfer_type"], unique=False)

    op.create_table(
        "approval_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.Enum("transfer", name="approvaltargettype"), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("requested_by_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("pending", "approved", "rejected", "cancelled", name="approvalstatus"), nullable=False),
        sa.Column("required_approvals", sa.Integer(), nullable=False),
        sa.Column("current_approvals", sa.Integer(), nullable=False),
        sa.Column("require_separate_approver", sa.Boolean(), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["requested_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"]),
        sa.UniqueConstraint("transfer_id"),
    )
    op.create_index(op.f("ix_approval_requests_created_at"), "approval_requests", ["created_at"], unique=False)
    op.create_index(op.f("ix_approval_requests_organization_id"), "approval_requests", ["organization_id"], unique=False)
    op.create_index(op.f("ix_approval_requests_requested_by_user_id"), "approval_requests", ["requested_by_user_id"], unique=False)
    op.create_index(op.f("ix_approval_requests_status"), "approval_requests", ["status"], unique=False)
    op.create_index(op.f("ix_approval_requests_target_type"), "approval_requests", ["target_type"], unique=False)
    op.create_index(op.f("ix_approval_requests_transfer_id"), "approval_requests", ["transfer_id"], unique=False)

    op.create_table(
        "approval_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("approval_request_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("decision", sa.Enum("approved", "rejected", name="approvaldecisiontype"), nullable=False),
        sa.Column("notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["approval_request_id"], ["approval_requests.id"]),
        sa.UniqueConstraint("approval_request_id", "actor_user_id", name="uq_approval_decision_actor"),
    )
    op.create_index(op.f("ix_approval_decisions_actor_user_id"), "approval_decisions", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_approval_decisions_approval_request_id"), "approval_decisions", ["approval_request_id"], unique=False)
    op.create_index(op.f("ix_approval_decisions_created_at"), "approval_decisions", ["created_at"], unique=False)
    op.create_index(op.f("ix_approval_decisions_decision"), "approval_decisions", ["decision"], unique=False)

    op.create_table(
        "risk_alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", sa.Enum("high_value_transfer", "external_transfer_review", "new_beneficiary_transfer", "kyc_review", "high_risk_customer", "transfer_velocity", name="riskalerttype"), nullable=False),
        sa.Column("severity", sa.Enum("low", "medium", "high", "critical", name="riskseverity"), nullable=False),
        sa.Column("status", sa.Enum("open", "in_review", "resolved", "dismissed", name="riskalertstatus"), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("assigned_to_user_id", sa.Integer(), nullable=True),
        sa.Column("resolved_by_user_id", sa.Integer(), nullable=True),
        sa.Column("resolution_notes", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["resolved_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_risk_alerts_account_id"), "risk_alerts", ["account_id"], unique=False)
    op.create_index(op.f("ix_risk_alerts_alert_type"), "risk_alerts", ["alert_type"], unique=False)
    op.create_index(op.f("ix_risk_alerts_assigned_to_user_id"), "risk_alerts", ["assigned_to_user_id"], unique=False)
    op.create_index(op.f("ix_risk_alerts_created_at"), "risk_alerts", ["created_at"], unique=False)
    op.create_index(op.f("ix_risk_alerts_organization_id"), "risk_alerts", ["organization_id"], unique=False)
    op.create_index(op.f("ix_risk_alerts_resolved_by_user_id"), "risk_alerts", ["resolved_by_user_id"], unique=False)
    op.create_index(op.f("ix_risk_alerts_rule_code"), "risk_alerts", ["rule_code"], unique=False)
    op.create_index(op.f("ix_risk_alerts_severity"), "risk_alerts", ["severity"], unique=False)
    op.create_index(op.f("ix_risk_alerts_status"), "risk_alerts", ["status"], unique=False)
    op.create_index(op.f("ix_risk_alerts_transfer_id"), "risk_alerts", ["transfer_id"], unique=False)
    op.create_index(op.f("ix_risk_alerts_user_id"), "risk_alerts", ["user_id"], unique=False)

    op.create_table(
        "compliance_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_number", sa.String(length=40), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.Enum("open", "in_review", "escalated", "closed", name="compliancecasestatus"), nullable=False),
        sa.Column("assigned_to_user_id", sa.Integer(), nullable=True),
        sa.Column("opened_by_user_id", sa.Integer(), nullable=True),
        sa.Column("closed_by_user_id", sa.Integer(), nullable=True),
        sa.Column("disposition", sa.String(length=120), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["alert_id"], ["risk_alerts.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["closed_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["opened_by_user_id"], ["users.id"]),
        sa.UniqueConstraint("alert_id"),
        sa.UniqueConstraint("case_number"),
    )
    op.create_index(op.f("ix_compliance_cases_alert_id"), "compliance_cases", ["alert_id"], unique=False)
    op.create_index(op.f("ix_compliance_cases_assigned_to_user_id"), "compliance_cases", ["assigned_to_user_id"], unique=False)
    op.create_index(op.f("ix_compliance_cases_case_number"), "compliance_cases", ["case_number"], unique=True)
    op.create_index(op.f("ix_compliance_cases_closed_by_user_id"), "compliance_cases", ["closed_by_user_id"], unique=False)
    op.create_index(op.f("ix_compliance_cases_created_at"), "compliance_cases", ["created_at"], unique=False)
    op.create_index(op.f("ix_compliance_cases_opened_by_user_id"), "compliance_cases", ["opened_by_user_id"], unique=False)
    op.create_index(op.f("ix_compliance_cases_status"), "compliance_cases", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_compliance_cases_status"), table_name="compliance_cases")
    op.drop_index(op.f("ix_compliance_cases_opened_by_user_id"), table_name="compliance_cases")
    op.drop_index(op.f("ix_compliance_cases_created_at"), table_name="compliance_cases")
    op.drop_index(op.f("ix_compliance_cases_closed_by_user_id"), table_name="compliance_cases")
    op.drop_index(op.f("ix_compliance_cases_case_number"), table_name="compliance_cases")
    op.drop_index(op.f("ix_compliance_cases_assigned_to_user_id"), table_name="compliance_cases")
    op.drop_index(op.f("ix_compliance_cases_alert_id"), table_name="compliance_cases")
    op.drop_table("compliance_cases")

    op.drop_index(op.f("ix_risk_alerts_user_id"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_transfer_id"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_status"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_severity"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_rule_code"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_resolved_by_user_id"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_organization_id"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_created_at"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_assigned_to_user_id"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_alert_type"), table_name="risk_alerts")
    op.drop_index(op.f("ix_risk_alerts_account_id"), table_name="risk_alerts")
    op.drop_table("risk_alerts")

    op.drop_index(op.f("ix_approval_decisions_decision"), table_name="approval_decisions")
    op.drop_index(op.f("ix_approval_decisions_created_at"), table_name="approval_decisions")
    op.drop_index(op.f("ix_approval_decisions_approval_request_id"), table_name="approval_decisions")
    op.drop_index(op.f("ix_approval_decisions_actor_user_id"), table_name="approval_decisions")
    op.drop_table("approval_decisions")

    op.drop_index(op.f("ix_approval_requests_transfer_id"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_target_type"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_status"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_requested_by_user_id"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_organization_id"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_created_at"), table_name="approval_requests")
    op.drop_table("approval_requests")

    op.drop_index(op.f("ix_approval_policies_transfer_type"), table_name="approval_policies")
    op.drop_index(op.f("ix_approval_policies_organization_id"), table_name="approval_policies")
    op.drop_index(op.f("ix_approval_policies_is_active"), table_name="approval_policies")
    op.drop_index(op.f("ix_approval_policies_created_by_user_id"), table_name="approval_policies")
    op.drop_table("approval_policies")
