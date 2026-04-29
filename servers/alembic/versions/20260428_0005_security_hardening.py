"""security hardening

Revision ID: 20260428_0005
Revises: 20260428_0004
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260428_0005"
down_revision = "20260428_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user_sessions") as batch_op:
        batch_op.add_column(sa.Column("device_fingerprint_hash", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("trusted_device", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("mfa_authenticated_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("step_up_expires_at", sa.DateTime(), nullable=True))
        batch_op.create_index(op.f("ix_user_sessions_device_fingerprint_hash"), ["device_fingerprint_hash"], unique=False)
        batch_op.create_index(op.f("ix_user_sessions_step_up_expires_at"), ["step_up_expires_at"], unique=False)

    op.create_table(
        "mfa_devices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("device_type", sa.String(length=40), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("secret_encrypted", sa.Text(), nullable=False),
        sa.Column("recovery_codes_hash", sa.Text(), nullable=True),
        sa.Column("is_confirmed", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(op.f("ix_mfa_devices_created_at"), "mfa_devices", ["created_at"], unique=False)
    op.create_index(op.f("ix_mfa_devices_is_active"), "mfa_devices", ["is_active"], unique=False)
    op.create_index(op.f("ix_mfa_devices_is_confirmed"), "mfa_devices", ["is_confirmed"], unique=False)
    op.create_index(op.f("ix_mfa_devices_user_id"), "mfa_devices", ["user_id"], unique=False)

    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=128), nullable=False),
        sa.Column("method", sa.String(length=12), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=False),
        sa.Column("resource_type", sa.String(length=80), nullable=True),
        sa.Column("resource_id", sa.String(length=80), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.UniqueConstraint("user_id", "key_hash", name="uq_idempotency_user_key"),
    )
    op.create_index(op.f("ix_idempotency_keys_created_at"), "idempotency_keys", ["created_at"], unique=False)
    op.create_index(op.f("ix_idempotency_keys_expires_at"), "idempotency_keys", ["expires_at"], unique=False)
    op.create_index(op.f("ix_idempotency_keys_key_hash"), "idempotency_keys", ["key_hash"], unique=False)
    op.create_index(op.f("ix_idempotency_keys_resource_id"), "idempotency_keys", ["resource_id"], unique=False)
    op.create_index(op.f("ix_idempotency_keys_resource_type"), "idempotency_keys", ["resource_type"], unique=False)
    op.create_index(op.f("ix_idempotency_keys_user_id"), "idempotency_keys", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_idempotency_keys_user_id"), table_name="idempotency_keys")
    op.drop_index(op.f("ix_idempotency_keys_resource_type"), table_name="idempotency_keys")
    op.drop_index(op.f("ix_idempotency_keys_resource_id"), table_name="idempotency_keys")
    op.drop_index(op.f("ix_idempotency_keys_key_hash"), table_name="idempotency_keys")
    op.drop_index(op.f("ix_idempotency_keys_expires_at"), table_name="idempotency_keys")
    op.drop_index(op.f("ix_idempotency_keys_created_at"), table_name="idempotency_keys")
    op.drop_table("idempotency_keys")

    op.drop_index(op.f("ix_mfa_devices_user_id"), table_name="mfa_devices")
    op.drop_index(op.f("ix_mfa_devices_is_confirmed"), table_name="mfa_devices")
    op.drop_index(op.f("ix_mfa_devices_is_active"), table_name="mfa_devices")
    op.drop_index(op.f("ix_mfa_devices_created_at"), table_name="mfa_devices")
    op.drop_table("mfa_devices")

    with op.batch_alter_table("user_sessions") as batch_op:
        batch_op.drop_index(op.f("ix_user_sessions_step_up_expires_at"))
        batch_op.drop_index(op.f("ix_user_sessions_device_fingerprint_hash"))
        batch_op.drop_column("step_up_expires_at")
        batch_op.drop_column("mfa_authenticated_at")
        batch_op.drop_column("trusted_device")
        batch_op.drop_column("device_fingerprint_hash")
