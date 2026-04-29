"""cards and disputes

Revision ID: 20260428_0004
Revises: 20260428_0003
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0004"
down_revision = "20260428_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("card_type", sa.Enum("debit", "credit", "virtual", name="cardtype"), nullable=False),
        sa.Column("network", sa.Enum("visa", "mastercard", name="cardnetwork"), nullable=False),
        sa.Column("status", sa.Enum("active", "frozen", "closed", "pending_activation", name="cardstatus"), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("last4", sa.String(length=4), nullable=False),
        sa.Column("expiry_month", sa.Integer(), nullable=False),
        sa.Column("expiry_year", sa.Integer(), nullable=False),
        sa.Column("daily_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("monthly_limit", sa.Numeric(14, 2), nullable=True),
        sa.Column("issued_at", sa.DateTime(), nullable=True),
        sa.Column("frozen_at", sa.DateTime(), nullable=True),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_cards_account_id"), "cards", ["account_id"], unique=False)
    op.create_index(op.f("ix_cards_issued_at"), "cards", ["issued_at"], unique=False)
    op.create_index(op.f("ix_cards_last4"), "cards", ["last4"], unique=False)
    op.create_index(op.f("ix_cards_organization_id"), "cards", ["organization_id"], unique=False)
    op.create_index(op.f("ix_cards_status"), "cards", ["status"], unique=False)
    op.create_index(op.f("ix_cards_user_id"), "cards", ["user_id"], unique=False)

    op.create_table(
        "card_controls",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("allow_online", sa.Boolean(), nullable=False),
        sa.Column("allow_international", sa.Boolean(), nullable=False),
        sa.Column("allow_atm", sa.Boolean(), nullable=False),
        sa.Column("blocked_merchant_categories", sa.String(length=500), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.UniqueConstraint("card_id"),
    )
    op.create_index(op.f("ix_card_controls_card_id"), "card_controls", ["card_id"], unique=True)

    op.create_table(
        "card_authorizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("merchant_name", sa.String(length=160), nullable=False),
        sa.Column("merchant_category", sa.String(length=80), nullable=False),
        sa.Column("merchant_country", sa.String(length=2), nullable=False),
        sa.Column("card_not_present", sa.Boolean(), nullable=False),
        sa.Column("status", sa.Enum("approved", "declined", "captured", "reversed", name="cardauthorizationstatus"), nullable=False),
        sa.Column("decline_reason", sa.String(length=255), nullable=True),
        sa.Column("authorized_at", sa.DateTime(), nullable=True),
        sa.Column("captured_at", sa.DateTime(), nullable=True),
        sa.Column("reversed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_card_authorizations_account_id"), "card_authorizations", ["account_id"], unique=False)
    op.create_index(op.f("ix_card_authorizations_authorized_at"), "card_authorizations", ["authorized_at"], unique=False)
    op.create_index(op.f("ix_card_authorizations_card_id"), "card_authorizations", ["card_id"], unique=False)
    op.create_index(op.f("ix_card_authorizations_organization_id"), "card_authorizations", ["organization_id"], unique=False)
    op.create_index(op.f("ix_card_authorizations_status"), "card_authorizations", ["status"], unique=False)
    op.create_index(op.f("ix_card_authorizations_transaction_id"), "card_authorizations", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_card_authorizations_user_id"), "card_authorizations", ["user_id"], unique=False)

    with op.batch_alter_table("account_holds") as batch_op:
        batch_op.add_column(sa.Column("card_authorization_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_account_holds_card_authorization_id", "card_authorizations", ["card_authorization_id"], ["id"])
        batch_op.create_index(op.f("ix_account_holds_card_authorization_id"), ["card_authorization_id"], unique=True)

    op.create_table(
        "disputes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("case_number", sa.String(length=40), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=False),
        sa.Column("transaction_id", sa.Integer(), nullable=True),
        sa.Column("card_authorization_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Enum("fraud", "duplicate", "goods_not_received", "incorrect_amount", "cancelled_service", "other", name="disputereason"), nullable=False),
        sa.Column("status", sa.Enum("open", "under_review", "provisional_credit", "won", "lost", "closed", name="disputestatus"), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("provisional_transaction_id", sa.Integer(), nullable=True),
        sa.Column("assigned_to_user_id", sa.Integer(), nullable=True),
        sa.Column("opened_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["assigned_to_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["card_authorization_id"], ["card_authorizations.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["provisional_transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("case_number"),
    )
    op.create_index(op.f("ix_disputes_account_id"), "disputes", ["account_id"], unique=False)
    op.create_index(op.f("ix_disputes_assigned_to_user_id"), "disputes", ["assigned_to_user_id"], unique=False)
    op.create_index(op.f("ix_disputes_card_authorization_id"), "disputes", ["card_authorization_id"], unique=False)
    op.create_index(op.f("ix_disputes_case_number"), "disputes", ["case_number"], unique=True)
    op.create_index(op.f("ix_disputes_opened_at"), "disputes", ["opened_at"], unique=False)
    op.create_index(op.f("ix_disputes_organization_id"), "disputes", ["organization_id"], unique=False)
    op.create_index(op.f("ix_disputes_provisional_transaction_id"), "disputes", ["provisional_transaction_id"], unique=False)
    op.create_index(op.f("ix_disputes_reason"), "disputes", ["reason"], unique=False)
    op.create_index(op.f("ix_disputes_status"), "disputes", ["status"], unique=False)
    op.create_index(op.f("ix_disputes_transaction_id"), "disputes", ["transaction_id"], unique=False)
    op.create_index(op.f("ix_disputes_user_id"), "disputes", ["user_id"], unique=False)

    op.create_table(
        "dispute_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dispute_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["dispute_id"], ["disputes.id"]),
    )
    op.create_index(op.f("ix_dispute_events_actor_user_id"), "dispute_events", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_dispute_events_created_at"), "dispute_events", ["created_at"], unique=False)
    op.create_index(op.f("ix_dispute_events_dispute_id"), "dispute_events", ["dispute_id"], unique=False)
    op.create_index(op.f("ix_dispute_events_event_type"), "dispute_events", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_dispute_events_event_type"), table_name="dispute_events")
    op.drop_index(op.f("ix_dispute_events_dispute_id"), table_name="dispute_events")
    op.drop_index(op.f("ix_dispute_events_created_at"), table_name="dispute_events")
    op.drop_index(op.f("ix_dispute_events_actor_user_id"), table_name="dispute_events")
    op.drop_table("dispute_events")

    op.drop_index(op.f("ix_disputes_user_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_transaction_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_status"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_reason"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_provisional_transaction_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_organization_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_opened_at"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_case_number"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_card_authorization_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_assigned_to_user_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_account_id"), table_name="disputes")
    op.drop_table("disputes")

    with op.batch_alter_table("account_holds") as batch_op:
        batch_op.drop_index(op.f("ix_account_holds_card_authorization_id"))
        batch_op.drop_constraint("fk_account_holds_card_authorization_id", type_="foreignkey")
        batch_op.drop_column("card_authorization_id")

    op.drop_index(op.f("ix_card_authorizations_user_id"), table_name="card_authorizations")
    op.drop_index(op.f("ix_card_authorizations_transaction_id"), table_name="card_authorizations")
    op.drop_index(op.f("ix_card_authorizations_status"), table_name="card_authorizations")
    op.drop_index(op.f("ix_card_authorizations_organization_id"), table_name="card_authorizations")
    op.drop_index(op.f("ix_card_authorizations_card_id"), table_name="card_authorizations")
    op.drop_index(op.f("ix_card_authorizations_authorized_at"), table_name="card_authorizations")
    op.drop_index(op.f("ix_card_authorizations_account_id"), table_name="card_authorizations")
    op.drop_table("card_authorizations")

    op.drop_index(op.f("ix_card_controls_card_id"), table_name="card_controls")
    op.drop_table("card_controls")

    op.drop_index(op.f("ix_cards_user_id"), table_name="cards")
    op.drop_index(op.f("ix_cards_status"), table_name="cards")
    op.drop_index(op.f("ix_cards_organization_id"), table_name="cards")
    op.drop_index(op.f("ix_cards_last4"), table_name="cards")
    op.drop_index(op.f("ix_cards_issued_at"), table_name="cards")
    op.drop_index(op.f("ix_cards_account_id"), table_name="cards")
    op.drop_table("cards")
