"""ledger holds statements and notifications

Revision ID: 20260428_0003
Revises: 20260428_0002
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0003"
down_revision = "20260428_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ledger_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("direction", sa.Enum("debit", "credit", name="ledgerdirection"), nullable=False),
        sa.Column("event_type", sa.Enum("opening_balance", "transfer_posted", "transaction_posted", "adjustment", name="ledgereventtype"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("effective_on", sa.Date(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"]),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index(op.f("ix_ledger_entries_account_id"), "ledger_entries", ["account_id"], unique=False)
    op.create_index(op.f("ix_ledger_entries_created_at"), "ledger_entries", ["created_at"], unique=False)
    op.create_index(op.f("ix_ledger_entries_created_by_user_id"), "ledger_entries", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_ledger_entries_direction"), "ledger_entries", ["direction"], unique=False)
    op.create_index(op.f("ix_ledger_entries_effective_on"), "ledger_entries", ["effective_on"], unique=False)
    op.create_index(op.f("ix_ledger_entries_event_type"), "ledger_entries", ["event_type"], unique=False)
    op.create_index(op.f("ix_ledger_entries_idempotency_key"), "ledger_entries", ["idempotency_key"], unique=True)
    op.create_index(op.f("ix_ledger_entries_organization_id"), "ledger_entries", ["organization_id"], unique=False)
    op.create_index(op.f("ix_ledger_entries_transaction_id"), "ledger_entries", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_ledger_entries_transfer_id"), "ledger_entries", ["transfer_id"], unique=False)

    op.create_table(
        "account_holds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("transfer_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("reason", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Enum("active", "released", "cancelled", "expired", name="holdstatus"), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["transfer_id"], ["transfers.id"]),
        sa.UniqueConstraint("transfer_id"),
    )
    op.create_index(op.f("ix_account_holds_account_id"), "account_holds", ["account_id"], unique=False)
    op.create_index(op.f("ix_account_holds_created_at"), "account_holds", ["created_at"], unique=False)
    op.create_index(op.f("ix_account_holds_created_by_user_id"), "account_holds", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_account_holds_expires_at"), "account_holds", ["expires_at"], unique=False)
    op.create_index(op.f("ix_account_holds_status"), "account_holds", ["status"], unique=False)
    op.create_index(op.f("ix_account_holds_transfer_id"), "account_holds", ["transfer_id"], unique=True)

    op.create_table(
        "account_balance_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("current_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("available_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("held_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.UniqueConstraint("account_id", "as_of_date", name="uq_account_balance_snapshot_date"),
    )
    op.create_index(op.f("ix_account_balance_snapshots_account_id"), "account_balance_snapshots", ["account_id"], unique=False)
    op.create_index(op.f("ix_account_balance_snapshots_as_of_date"), "account_balance_snapshots", ["as_of_date"], unique=False)
    op.create_index(op.f("ix_account_balance_snapshots_created_at"), "account_balance_snapshots", ["created_at"], unique=False)

    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("notification_type", sa.Enum("transfer", "approval", "risk", "statement", "system", name="notificationtype"), nullable=False),
        sa.Column("priority", sa.Enum("info", "action_required", "warning", "critical", name="notificationpriority"), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("action_url", sa.String(length=255), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_notifications_created_at"), "notifications", ["created_at"], unique=False)
    op.create_index(op.f("ix_notifications_notification_type"), "notifications", ["notification_type"], unique=False)
    op.create_index(op.f("ix_notifications_organization_id"), "notifications", ["organization_id"], unique=False)
    op.create_index(op.f("ix_notifications_priority"), "notifications", ["priority"], unique=False)
    op.create_index(op.f("ix_notifications_read_at"), "notifications", ["read_at"], unique=False)
    op.create_index(op.f("ix_notifications_user_id"), "notifications", ["user_id"], unique=False)

    op.create_table(
        "account_statements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("opening_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("closing_balance", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_debits", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_credits", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.Enum("generated", "voided", name="statementstatus"), nullable=False),
        sa.Column("generated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("generated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["generated_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("account_id", "period_start", "period_end", name="uq_statement_account_period"),
    )
    op.create_index(op.f("ix_account_statements_account_id"), "account_statements", ["account_id"], unique=False)
    op.create_index(op.f("ix_account_statements_generated_at"), "account_statements", ["generated_at"], unique=False)
    op.create_index(op.f("ix_account_statements_generated_by_user_id"), "account_statements", ["generated_by_user_id"], unique=False)
    op.create_index(op.f("ix_account_statements_organization_id"), "account_statements", ["organization_id"], unique=False)
    op.create_index(op.f("ix_account_statements_period_end"), "account_statements", ["period_end"], unique=False)
    op.create_index(op.f("ix_account_statements_period_start"), "account_statements", ["period_start"], unique=False)
    op.create_index(op.f("ix_account_statements_status"), "account_statements", ["status"], unique=False)
    op.create_index(op.f("ix_account_statements_user_id"), "account_statements", ["user_id"], unique=False)

    op.create_table(
        "account_statement_lines",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("statement_id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("ledger_entry_id", sa.Integer(), nullable=True),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("debit", sa.Numeric(14, 2), nullable=False),
        sa.Column("credit", sa.Numeric(14, 2), nullable=False),
        sa.Column("running_balance", sa.Numeric(14, 2), nullable=False),
        sa.ForeignKeyConstraint(["ledger_entry_id"], ["ledger_entries.id"]),
        sa.ForeignKeyConstraint(["statement_id"], ["account_statements.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
    )
    op.create_index(op.f("ix_account_statement_lines_ledger_entry_id"), "account_statement_lines", ["ledger_entry_id"], unique=False)
    op.create_index(op.f("ix_account_statement_lines_occurred_on"), "account_statement_lines", ["occurred_on"], unique=False)
    op.create_index(op.f("ix_account_statement_lines_statement_id"), "account_statement_lines", ["statement_id"], unique=False)
    op.create_index(op.f("ix_account_statement_lines_transaction_id"), "account_statement_lines", ["transaction_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_account_statement_lines_transaction_id"), table_name="account_statement_lines")
    op.drop_index(op.f("ix_account_statement_lines_statement_id"), table_name="account_statement_lines")
    op.drop_index(op.f("ix_account_statement_lines_occurred_on"), table_name="account_statement_lines")
    op.drop_index(op.f("ix_account_statement_lines_ledger_entry_id"), table_name="account_statement_lines")
    op.drop_table("account_statement_lines")

    op.drop_index(op.f("ix_account_statements_user_id"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_status"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_period_start"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_period_end"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_organization_id"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_generated_by_user_id"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_generated_at"), table_name="account_statements")
    op.drop_index(op.f("ix_account_statements_account_id"), table_name="account_statements")
    op.drop_table("account_statements")

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_read_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_priority"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_organization_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_notification_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_table("notifications")

    op.drop_index(op.f("ix_account_balance_snapshots_created_at"), table_name="account_balance_snapshots")
    op.drop_index(op.f("ix_account_balance_snapshots_as_of_date"), table_name="account_balance_snapshots")
    op.drop_index(op.f("ix_account_balance_snapshots_account_id"), table_name="account_balance_snapshots")
    op.drop_table("account_balance_snapshots")

    op.drop_index(op.f("ix_account_holds_transfer_id"), table_name="account_holds")
    op.drop_index(op.f("ix_account_holds_status"), table_name="account_holds")
    op.drop_index(op.f("ix_account_holds_expires_at"), table_name="account_holds")
    op.drop_index(op.f("ix_account_holds_created_by_user_id"), table_name="account_holds")
    op.drop_index(op.f("ix_account_holds_created_at"), table_name="account_holds")
    op.drop_index(op.f("ix_account_holds_account_id"), table_name="account_holds")
    op.drop_table("account_holds")

    op.drop_index(op.f("ix_ledger_entries_transfer_id"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_transaction_id"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_organization_id"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_idempotency_key"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_event_type"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_effective_on"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_direction"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_created_by_user_id"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_created_at"), table_name="ledger_entries")
    op.drop_index(op.f("ix_ledger_entries_account_id"), table_name="ledger_entries")
    op.drop_table("ledger_entries")
