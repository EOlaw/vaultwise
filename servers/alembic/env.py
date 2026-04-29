from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from app.config import get_settings
from app.database import Base
from app.audit.models import AuditLog, SecurityEvent
from app.auth.models import LoginAttempt, RefreshToken, UserSession
from app.accounts.models import Account
from app.approvals.models import ApprovalDecision, ApprovalPolicy, ApprovalRequest
from app.budgets.models import Budget
from app.cards.models import Card, CardAuthorization, CardControl
from app.disputes.models import Dispute, DisputeEvent
from app.iam.models import Permission, PolicyDecision, Role, RolePermission, UserRoleAssignment
from app.ledger.models import AccountBalanceSnapshot, AccountHold, LedgerEntry
from app.notifications.models import Notification
from app.organizations.models import AccountEntitlement, Organization, OrganizationMembership
from app.risk.models import ComplianceCase, RiskAlert
from app.statements.models import AccountStatement, AccountStatementLine
from app.transactions.models import Transaction
from app.transfers.models import Beneficiary, Transfer, TransferEvent
from app.users.models import User, UserProfile


config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=get_settings().database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
