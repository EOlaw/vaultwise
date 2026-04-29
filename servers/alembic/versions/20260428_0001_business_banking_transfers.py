"""business banking organizations and money movement

Revision ID: 20260428_0001
Revises:
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("legal_name", sa.String(length=200), nullable=False),
        sa.Column("organization_type", sa.Enum("business", "nonprofit", "internal", name="organizationtype"), nullable=False),
        sa.Column("status", sa.Enum("active", "suspended", "closed", name="organizationstatus"), nullable=False),
        sa.Column("tax_id_last4", sa.String(length=4), nullable=True),
        sa.Column("industry", sa.String(length=120), nullable=True),
        sa.Column("phone", sa.String(length=40), nullable=True),
        sa.Column("address_line1", sa.String(length=180), nullable=True),
        sa.Column("address_line2", sa.String(length=180), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=80), nullable=True),
        sa.Column("postal_code", sa.String(length=20), nullable=True),
        sa.Column("country", sa.String(length=80), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"], unique=False)
    op.create_index(op.f("ix_organizations_status"), "organizations", ["status"], unique=False)
    op.create_index(op.f("ix_organizations_created_by_user_id"), "organizations", ["created_by_user_id"], unique=False)

    with op.batch_alter_table("accounts") as batch_op:
        batch_op.add_column(sa.Column("organization_id", sa.Integer(), nullable=True))
        batch_op.create_index(op.f("ix_accounts_organization_id"), ["organization_id"], unique=False)
        batch_op.create_foreign_key("fk_accounts_organization_id_organizations", "organizations", ["organization_id"], ["id"])

    op.create_table(
        "organization_memberships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.Enum("owner", "admin", "operator", "approver", "viewer", name="membershiprole"), nullable=False),
        sa.Column("status", sa.Enum("active", "invited", "suspended", "removed", name="membershipstatus"), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=True),
        sa.Column("can_invite_members", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_membership_user"),
    )
    op.create_index(op.f("ix_organization_memberships_organization_id"), "organization_memberships", ["organization_id"], unique=False)
    op.create_index(op.f("ix_organization_memberships_status"), "organization_memberships", ["status"], unique=False)
    op.create_index(op.f("ix_organization_memberships_user_id"), "organization_memberships", ["user_id"], unique=False)

    op.create_table(
        "account_entitlements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("can_view", sa.Boolean(), nullable=False),
        sa.Column("can_transact", sa.Boolean(), nullable=False),
        sa.Column("can_approve", sa.Boolean(), nullable=False),
        sa.Column("daily_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("monthly_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.Enum("active", "revoked", name="entitlementstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("organization_id", "account_id", "user_id", name="uq_org_account_user_entitlement"),
    )
    op.create_index(op.f("ix_account_entitlements_account_id"), "account_entitlements", ["account_id"], unique=False)
    op.create_index(op.f("ix_account_entitlements_organization_id"), "account_entitlements", ["organization_id"], unique=False)
    op.create_index(op.f("ix_account_entitlements_status"), "account_entitlements", ["status"], unique=False)
    op.create_index(op.f("ix_account_entitlements_user_id"), "account_entitlements", ["user_id"], unique=False)

    op.create_table(
        "beneficiaries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("beneficiary_type", sa.Enum("internal_account", "external_ach", "wire", "bill_pay", name="beneficiarytype"), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("bank_name", sa.String(length=160), nullable=True),
        sa.Column("routing_number_last4", sa.String(length=4), nullable=True),
        sa.Column("account_number_last4", sa.String(length=4), nullable=True),
        sa.Column("internal_account_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.Enum("active", "inactive", "blocked", name="beneficiarystatus"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["internal_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_beneficiaries_created_by_user_id"), "beneficiaries", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_beneficiaries_internal_account_id"), "beneficiaries", ["internal_account_id"], unique=False)
    op.create_index(op.f("ix_beneficiaries_organization_id"), "beneficiaries", ["organization_id"], unique=False)
    op.create_index(op.f("ix_beneficiaries_owner_user_id"), "beneficiaries", ["owner_user_id"], unique=False)
    op.create_index(op.f("ix_beneficiaries_status"), "beneficiaries", ["status"], unique=False)

    op.create_table(
        "transfers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("from_account_id", sa.Integer(), nullable=False),
        sa.Column("to_account_id", sa.Integer(), nullable=True),
        sa.Column("beneficiary_id", sa.Integer(), nullable=True),
        sa.Column("transfer_type", sa.Enum("internal", "external_ach", "wire", "bill_pay", name="transfertype"), nullable=False),
        sa.Column("status", sa.Enum("draft", "pending_approval", "scheduled", "processing", "posted", "cancelled", "rejected", "failed", name="transferstatus"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("memo", sa.String(length=255), nullable=True),
        sa.Column("requested_on", sa.Date(), nullable=True),
        sa.Column("scheduled_for", sa.Date(), nullable=True),
        sa.Column("posted_at", sa.DateTime(), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["beneficiary_id"], ["beneficiaries.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["from_account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["to_account_id"], ["accounts.id"]),
    )
    op.create_index(op.f("ix_transfers_beneficiary_id"), "transfers", ["beneficiary_id"], unique=False)
    op.create_index(op.f("ix_transfers_created_by_user_id"), "transfers", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_transfers_from_account_id"), "transfers", ["from_account_id"], unique=False)
    op.create_index(op.f("ix_transfers_organization_id"), "transfers", ["organization_id"], unique=False)
    op.create_index(op.f("ix_transfers_requested_on"), "transfers", ["requested_on"], unique=False)
    op.create_index(op.f("ix_transfers_scheduled_for"), "transfers", ["scheduled_for"], unique=False)
    op.create_index(op.f("ix_transfers_status"), "transfers", ["status"], unique=False)
    op.create_index(op.f("ix_transfers_to_account_id"), "transfers", ["to_account_id"], unique=False)

    op.create_table(
        "transfer_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transfer_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"]),
    )
    op.create_index(op.f("ix_transfer_events_actor_user_id"), "transfer_events", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_transfer_events_created_at"), "transfer_events", ["created_at"], unique=False)
    op.create_index(op.f("ix_transfer_events_event_type"), "transfer_events", ["event_type"], unique=False)
    op.create_index(op.f("ix_transfer_events_transfer_id"), "transfer_events", ["transfer_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_transfer_events_transfer_id"), table_name="transfer_events")
    op.drop_index(op.f("ix_transfer_events_event_type"), table_name="transfer_events")
    op.drop_index(op.f("ix_transfer_events_created_at"), table_name="transfer_events")
    op.drop_index(op.f("ix_transfer_events_actor_user_id"), table_name="transfer_events")
    op.drop_table("transfer_events")

    op.drop_index(op.f("ix_transfers_to_account_id"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_status"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_scheduled_for"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_requested_on"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_organization_id"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_from_account_id"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_created_by_user_id"), table_name="transfers")
    op.drop_index(op.f("ix_transfers_beneficiary_id"), table_name="transfers")
    op.drop_table("transfers")

    op.drop_index(op.f("ix_beneficiaries_status"), table_name="beneficiaries")
    op.drop_index(op.f("ix_beneficiaries_owner_user_id"), table_name="beneficiaries")
    op.drop_index(op.f("ix_beneficiaries_organization_id"), table_name="beneficiaries")
    op.drop_index(op.f("ix_beneficiaries_internal_account_id"), table_name="beneficiaries")
    op.drop_index(op.f("ix_beneficiaries_created_by_user_id"), table_name="beneficiaries")
    op.drop_table("beneficiaries")

    op.drop_index(op.f("ix_account_entitlements_user_id"), table_name="account_entitlements")
    op.drop_index(op.f("ix_account_entitlements_status"), table_name="account_entitlements")
    op.drop_index(op.f("ix_account_entitlements_organization_id"), table_name="account_entitlements")
    op.drop_index(op.f("ix_account_entitlements_account_id"), table_name="account_entitlements")
    op.drop_table("account_entitlements")

    op.drop_index(op.f("ix_organization_memberships_user_id"), table_name="organization_memberships")
    op.drop_index(op.f("ix_organization_memberships_status"), table_name="organization_memberships")
    op.drop_index(op.f("ix_organization_memberships_organization_id"), table_name="organization_memberships")
    op.drop_table("organization_memberships")

    with op.batch_alter_table("accounts") as batch_op:
        batch_op.drop_constraint("fk_accounts_organization_id_organizations", type_="foreignkey")
        batch_op.drop_index(op.f("ix_accounts_organization_id"))
        batch_op.drop_column("organization_id")

    op.drop_index(op.f("ix_organizations_created_by_user_id"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_status"), table_name="organizations")
    op.drop_index(op.f("ix_organizations_name"), table_name="organizations")
    op.drop_table("organizations")
