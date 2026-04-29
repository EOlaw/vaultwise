"""enterprise card controls

Revision ID: 20260428_0006
Revises: 20260428_0005
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0006"
down_revision = "20260428_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TYPE cardtype ADD VALUE IF NOT EXISTS 'savings'")

    with op.batch_alter_table("cards") as batch_op:
        batch_op.add_column(sa.Column("card_token_hash", sa.String(length=128), nullable=True))

    op.execute("UPDATE cards SET card_token_hash = 'legacy-' || id || '-' || last4 WHERE card_token_hash IS NULL")
    op.create_index(op.f("ix_cards_card_token_hash"), "cards", ["card_token_hash"], unique=True)

    with op.batch_alter_table("card_controls") as batch_op:
        batch_op.add_column(sa.Column("allow_card_present", sa.Boolean(), server_default=sa.true(), nullable=False))
        batch_op.add_column(sa.Column("allow_contactless", sa.Boolean(), server_default=sa.true(), nullable=False))
        batch_op.add_column(sa.Column("require_pin", sa.Boolean(), server_default=sa.false(), nullable=False))
        batch_op.add_column(sa.Column("max_transaction_amount", sa.Numeric(14, 2), nullable=True))

    channel_enum = sa.Enum("card_present", "online", "contactless", "atm", name="cardtransactionchannel")
    if bind.dialect.name != "postgresql":
        channel_enum.create(bind, checkfirst=True)

    with op.batch_alter_table("card_authorizations") as batch_op:
        batch_op.add_column(sa.Column("channel", channel_enum, server_default="online", nullable=False))


def downgrade() -> None:
    with op.batch_alter_table("card_authorizations") as batch_op:
        batch_op.drop_column("channel")

    with op.batch_alter_table("card_controls") as batch_op:
        batch_op.drop_column("max_transaction_amount")
        batch_op.drop_column("require_pin")
        batch_op.drop_column("allow_contactless")
        batch_op.drop_column("allow_card_present")

    op.drop_index(op.f("ix_cards_card_token_hash"), table_name="cards")
    with op.batch_alter_table("cards") as batch_op:
        batch_op.drop_column("card_token_hash")
