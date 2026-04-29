from datetime import date
from decimal import Decimal
from sqlalchemy import select
from app.accounts.models import Account, AccountType
from app.accounts.schemas import AccountCreate
from app.accounts.service import create_account
from app.approvals.models import ApprovalPolicy, ApprovalRequest
from app.approvals.service import ensure_transfer_approval_request, transfer_approval_requirement
from app.budgets.models import Budget
from app.budgets.schemas import BudgetCreate
from app.budgets.service import create_budget
from app.cards.models import Card, CardAuthorization, CardAuthorizationStatus
from app.cards.schemas import CardAuthorizationCreate, CardControlUpdate, CardCreate
from app.cards.service import authorize_card, capture_authorization, create_card, update_controls
from app.database import Base, SessionLocal, engine
from app.disputes.models import Dispute, DisputeReason, DisputeStatus
from app.disputes.schemas import DisputeCreate, DisputeStatusUpdate
from app.disputes.service import create_dispute, update_dispute_status
from app.iam.models import Role, UserRoleAssignment
from app.iam.service import assign_role, bootstrap_iam, sync_legacy_user_role
from app.ledger.service import create_hold_for_transfer, record_transaction_ledger_entry, record_transfer_ledger_entries, snapshot_account_balance
from app.organizations.models import (
    AccountEntitlement,
    EntitlementStatus,
    MembershipRole,
    MembershipStatus,
    Organization,
    OrganizationMembership,
    OrganizationType,
)
from app.transactions.models import Transaction, TransactionType
from app.transactions.schemas import TransactionCreate
from app.transactions.service import create_transaction
from app.risk.service import alerts_require_approval, screen_transfer
from app.statements.schemas import StatementGenerateRequest
from app.statements.service import generate_statement
from app.transfers.models import Beneficiary, BeneficiaryType, Transfer, TransferStatus, TransferType
from app.transfers.schemas import BeneficiaryCreate, TransferCreate
from app.transfers.service import create_beneficiary, create_transfer, submit_transfer
from app.users.models import CustomerType, KycStatus, RiskRating, User, UserProfile, UserRole
from app.users.schemas import UserCreate
from app.users.service import create_user, get_by_email
from app.utils.dev_migrations import ensure_sqlite_development_schema


TEST_PASSWORD = "password123"


DEMO_USERS = [
    {
        "email": "admin@example.com",
        "name": "Admin User",
        "legacy_role": UserRole.admin,
        "roles": ["super_admin"],
        "profile": {
            "customer_reference": "INT-0001",
            "customer_type": CustomerType.internal,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0101",
            "occupation": "Platform Administrator",
            "employer_name": "BankOS",
            "address_line1": "100 BankOS Plaza",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "notes": "Full system administrator for smoke testing privileged endpoints.",
        },
        "banking": "business",
    },
    {
        "email": "bank.admin@bankos.com",
        "name": "Jordan Ellis",
        "roles": ["bank_admin"],
        "profile": {
            "customer_reference": "INT-0002",
            "customer_type": CustomerType.internal,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0102",
            "occupation": "Bank Operations Manager",
            "employer_name": "BankOS",
            "address_line1": "100 BankOS Plaza",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "notes": "Can review users, accounts, reports, audit data, and operational metrics.",
        },
    },
    {
        "email": "compliance@bankos.com",
        "name": "Priya Shah",
        "roles": ["compliance_officer"],
        "profile": {
            "customer_reference": "INT-0003",
            "customer_type": CustomerType.internal,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0103",
            "occupation": "Compliance Officer",
            "employer_name": "BankOS",
            "address_line1": "100 BankOS Plaza",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "notes": "Audit and compliance review user.",
        },
    },
    {
        "email": "risk@bankos.com",
        "name": "Miles Carter",
        "roles": ["risk_manager"],
        "profile": {
            "customer_reference": "INT-0004",
            "customer_type": CustomerType.internal,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0104",
            "occupation": "Risk Manager",
            "employer_name": "BankOS",
            "address_line1": "100 BankOS Plaza",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "notes": "Risk analytics and exposure review user.",
        },
    },
    {
        "email": "support@bankos.com",
        "name": "Taylor Reed",
        "roles": ["support_agent"],
        "profile": {
            "customer_reference": "INT-0005",
            "customer_type": CustomerType.internal,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0105",
            "occupation": "Customer Support Agent",
            "employer_name": "BankOS",
            "address_line1": "100 BankOS Plaza",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60601",
            "notes": "Read-focused support user for account and transaction troubleshooting.",
        },
    },
    {
        "email": "owner@acme.com",
        "name": "Morgan Alvarez",
        "roles": ["business_owner"],
        "profile": {
            "customer_reference": "BUS-1001",
            "customer_type": CustomerType.business,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.medium,
            "phone": "+1-312-555-0201",
            "date_of_birth": date(1987, 5, 14),
            "occupation": "Founder",
            "business_name": "Acme Design Studio LLC",
            "annual_income": Decimal("245000"),
            "address_line1": "455 W Lake Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60606",
            "notes": "Business owner with operating accounts, card exposure, recurring expenses, and budgets.",
        },
        "banking": "business",
    },
    {
        "email": "accountant@acme.com",
        "name": "Nina Brooks",
        "roles": ["accountant"],
        "profile": {
            "customer_reference": "BUS-1002",
            "customer_type": CustomerType.business,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0202",
            "occupation": "Accountant",
            "business_name": "Acme Design Studio LLC",
            "annual_income": Decimal("118000"),
            "address_line1": "455 W Lake Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60606",
            "notes": "Accountant persona for report export and read-only ledger review.",
        },
        "banking": "accountant",
    },
    {
        "email": "approver@acme.com",
        "name": "Elliot Grant",
        "roles": ["business_admin"],
        "profile": {
            "customer_reference": "BUS-1003",
            "customer_type": CustomerType.business,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0203",
            "occupation": "Operations Approver",
            "business_name": "Acme Design Studio LLC",
            "annual_income": Decimal("154000"),
            "address_line1": "455 W Lake Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60606",
            "notes": "Business approver persona for dual-control transfer approval testing.",
        },
        "banking": "approver",
    },
    {
        "email": "customer@bankos.com",
        "name": "Avery Johnson",
        "roles": ["customer"],
        "profile": {
            "customer_reference": "PER-2001",
            "customer_type": CustomerType.personal,
            "kyc_status": KycStatus.verified,
            "risk_rating": RiskRating.low,
            "phone": "+1-312-555-0301",
            "date_of_birth": date(1992, 9, 22),
            "occupation": "Product Manager",
            "employer_name": "Northwind Apps",
            "annual_income": Decimal("132000"),
            "address_line1": "712 N Wells Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60654",
            "notes": "Personal banking customer with checking, savings, card, and student loan records.",
        },
        "banking": "personal",
    },
    {
        "email": "readonly@bankos.com",
        "name": "Samir Patel",
        "roles": ["read_only"],
        "profile": {
            "customer_reference": "PER-2002",
            "customer_type": CustomerType.personal,
            "kyc_status": KycStatus.pending,
            "risk_rating": RiskRating.medium,
            "phone": "+1-312-555-0302",
            "date_of_birth": date(1984, 1, 8),
            "occupation": "Consultant",
            "annual_income": Decimal("98000"),
            "address_line1": "220 S State Street",
            "city": "Chicago",
            "state": "IL",
            "postal_code": "60604",
            "notes": "Read-only persona to confirm RBAC denial on create/update/delete actions.",
        },
        "banking": "personal_readonly",
    },
]


def ensure_user(db, spec: dict):
    user = get_by_email(db, spec["email"])
    if not user:
        user = create_user(
            db,
            UserCreate(
                email=spec["email"],
                full_name=spec["name"],
                password=TEST_PASSWORD,
                role=spec.get("legacy_role", UserRole.user),
            ),
        )
    bootstrap_iam(db)
    sync_legacy_user_role(db, user)
    replace_user_roles(db, user_id=user.id, role_names=spec["roles"], assigned_by_user_id=1 if user.id != 1 else None)
    ensure_profile(db, user.id, spec["profile"])
    return user


def replace_user_roles(db, *, user_id: int, role_names: list[str], assigned_by_user_id: int | None = None) -> None:
    roles = db.scalars(select(Role).where(Role.name.in_(role_names))).all()
    desired_role_ids = {role.id for role in roles}
    assignments = db.scalars(select(UserRoleAssignment).where(UserRoleAssignment.user_id == user_id)).all()
    for assignment in assignments:
        if assignment.role_id not in desired_role_ids:
            db.delete(assignment)
    db.commit()
    for role_name in role_names:
        assign_role(db, user_id=user_id, role_name=role_name, assigned_by_user_id=assigned_by_user_id)


def ensure_profile(db, user_id: int, profile: dict) -> None:
    existing = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    if existing:
        for key, value in profile.items():
            setattr(existing, key, value)
    else:
        db.add(UserProfile(user_id=user_id, **profile))
    db.commit()


def ensure_account_entitlement(
    db,
    *,
    organization_id: int,
    account_id: int,
    user_id: int,
    can_view: bool = True,
    can_transact: bool = False,
    can_approve: bool = False,
) -> AccountEntitlement:
    entitlement = db.scalar(
        select(AccountEntitlement).where(
            AccountEntitlement.organization_id == organization_id,
            AccountEntitlement.account_id == account_id,
            AccountEntitlement.user_id == user_id,
        )
    )
    if entitlement:
        entitlement.can_view = can_view
        entitlement.can_transact = can_transact
        entitlement.can_approve = can_approve
        entitlement.status = EntitlementStatus.active
        entitlement.revoked_at = None
    else:
        entitlement = AccountEntitlement(
            organization_id=organization_id,
            account_id=account_id,
            user_id=user_id,
            can_view=can_view,
            can_transact=can_transact,
            can_approve=can_approve,
            status=EntitlementStatus.active,
        )
        db.add(entitlement)
    db.commit()
    db.refresh(entitlement)
    return entitlement


def ensure_account(db, user_id: int, payload: AccountCreate):
    organization_id = payload.organization_id
    account = db.scalar(
        select(Account).where(
            Account.user_id == user_id,
            Account.name == payload.name,
            Account.organization_id == organization_id,
        )
    )
    if account:
        return account
    if organization_id is not None:
        legacy_account = db.scalar(
            select(Account).where(
                Account.user_id == user_id,
                Account.name == payload.name,
                Account.organization_id.is_(None),
            )
        )
        if legacy_account:
            legacy_account.organization_id = organization_id
            db.commit()
            db.refresh(legacy_account)
            ensure_account_entitlement(
                db,
                organization_id=organization_id,
                account_id=legacy_account.id,
                user_id=user_id,
                can_view=True,
                can_transact=True,
                can_approve=True,
            )
            return legacy_account
    return create_account(db, user_id, payload)


def ensure_card(
    db,
    user: User,
    account: Account,
    *,
    display_name: str,
    daily_limit: Decimal,
    monthly_limit: Decimal,
    blocked_merchant_categories: str | None = None,
) -> Card:
    card = db.scalar(select(Card).where(Card.account_id == account.id, Card.display_name == display_name))
    if card:
        card.daily_limit = daily_limit
        card.monthly_limit = monthly_limit
        db.commit()
        db.refresh(card)
    else:
        card = create_card(
            db,
            user,
            CardCreate(
                account_id=account.id,
                display_name=display_name,
                daily_limit=daily_limit,
                monthly_limit=monthly_limit,
            ),
        )
    update_controls(
        db,
        user,
        card.id,
        CardControlUpdate(
            allow_online=True,
            allow_international=False,
            allow_atm=True,
            blocked_merchant_categories=blocked_merchant_categories,
        ),
    )
    db.refresh(card)
    return card


def ensure_card_authorization(
    db,
    user: User,
    card: Card,
    *,
    amount: Decimal,
    merchant_name: str,
    merchant_category: str,
    capture: bool = True,
) -> CardAuthorization:
    authorization = db.scalar(
        select(CardAuthorization).where(
            CardAuthorization.card_id == card.id,
            CardAuthorization.amount == amount,
            CardAuthorization.merchant_name == merchant_name,
            CardAuthorization.merchant_category == merchant_category,
        )
    )
    if not authorization:
        authorization = authorize_card(
            db,
            user,
            CardAuthorizationCreate(
                card_id=card.id,
                amount=amount,
                merchant_name=merchant_name,
                merchant_category=merchant_category,
                card_not_present=True,
            ),
        )
    if capture and authorization.status == CardAuthorizationStatus.approved:
        authorization = capture_authorization(db, user, authorization.id)
    return authorization


def ensure_dispute_for_card_authorization(
    db,
    user: User,
    staff_user: User | None,
    authorization: CardAuthorization,
    *,
    reason: DisputeReason,
    amount: Decimal,
    description: str,
) -> Dispute:
    dispute = db.scalar(
        select(Dispute).where(
            Dispute.card_authorization_id == authorization.id,
            Dispute.reason == reason,
        )
    )
    if not dispute:
        dispute = create_dispute(
            db,
            user,
            DisputeCreate(
                card_authorization_id=authorization.id,
                reason=reason,
                amount=amount,
                description=description,
            ),
        )
    if staff_user and dispute.status == DisputeStatus.open:
        dispute = update_dispute_status(
            db,
            staff_user,
            dispute.id,
            DisputeStatusUpdate(status=DisputeStatus.provisional_credit, notes="Seeded provisional credit for dispute review."),
        )
    return dispute


def ensure_transaction_set(db, user_id: int, account_id: int, samples: list[tuple[str, str, int, date, str | None]]) -> None:
    if db.scalar(select(Transaction).where(Transaction.user_id == user_id)):
        for transaction in db.scalars(select(Transaction).where(Transaction.user_id == user_id)).all():
            record_transaction_ledger_entry(db, transaction, actor_user_id=user_id)
        db.commit()
        return
    for kind, category, amount, occurred_on, recurring in samples:
        create_transaction(
            db,
            user_id,
            TransactionCreate(
                account_id=account_id,
                type=TransactionType(kind),
                amount=Decimal(str(amount)),
                occurred_on=occurred_on,
                category=category,
                recurring_rule=recurring,
            ),
        )


def ensure_budgets(db, user_id: int, items: list[tuple[str, int]]) -> None:
    for category, limit in items:
        exists = db.scalar(select(Budget).where(Budget.user_id == user_id, Budget.month == "2026-04", Budget.category == category))
        if not exists:
            create_budget(db, user_id, BudgetCreate(month="2026-04", category=category, limit_amount=Decimal(str(limit))))


def ensure_organization(db, owner_user_id: int) -> Organization:
    organization = db.scalar(select(Organization).where(Organization.legal_name == "Acme Design Studio LLC"))
    if organization:
        return organization
    organization = Organization(
        name="Acme Design Studio",
        legal_name="Acme Design Studio LLC",
        organization_type=OrganizationType.business,
        tax_id_last4="4821",
        industry="Creative services",
        phone="+1-312-555-0200",
        address_line1="455 W Lake Street",
        city="Chicago",
        state="IL",
        postal_code="60606",
        country="United States",
        created_by_user_id=owner_user_id,
    )
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def ensure_membership(db, *, organization_id: int, user_id: int, role: MembershipRole, title: str, can_invite_members: bool = False) -> OrganizationMembership:
    membership = db.scalar(
        select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
        )
    )
    if membership:
        membership.role = role
        membership.status = MembershipStatus.active
        membership.title = title
        membership.can_invite_members = can_invite_members
    else:
        membership = OrganizationMembership(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
            status=MembershipStatus.active,
            title=title,
            can_invite_members=can_invite_members,
        )
        db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership


def ensure_approval_policy(db, *, organization_id: int, user_id: int) -> ApprovalPolicy:
    policy = db.scalar(
        select(ApprovalPolicy).where(
            ApprovalPolicy.organization_id == organization_id,
            ApprovalPolicy.name == "Acme dual-control threshold",
        )
    )
    if policy:
        policy.min_amount = Decimal("1000.00")
        policy.required_approvals = 1
        policy.require_separate_approver = True
        policy.is_active = True
    else:
        policy = ApprovalPolicy(
            organization_id=organization_id,
            name="Acme dual-control threshold",
            min_amount=Decimal("1000.00"),
            required_approvals=1,
            require_separate_approver=True,
            is_active=True,
            created_by_user_id=user_id,
        )
        db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def seed_business_card_activity(db, owner: User, support_agent: User | None, checking: Account) -> None:
    card = ensure_card(
        db,
        owner,
        checking,
        display_name="Acme Operations Visa",
        daily_limit=Decimal("1500.00"),
        monthly_limit=Decimal("7500.00"),
        blocked_merchant_categories="Gambling,Cash Advance",
    )
    authorization = ensure_card_authorization(
        db,
        owner,
        card,
        amount=Decimal("145.37"),
        merchant_name="Midwest Office Supply",
        merchant_category="Office Supplies",
    )
    ensure_card_authorization(
        db,
        owner,
        card,
        amount=Decimal("42.18"),
        merchant_name="Loop Coffee Roasters",
        merchant_category="Meals",
    )
    ensure_dispute_for_card_authorization(
        db,
        owner,
        support_agent,
        authorization,
        reason=DisputeReason.incorrect_amount,
        amount=Decimal("45.37"),
        description="Vendor receipt shows a lower amount than the captured card authorization.",
    )


def seed_business_banking(db, owner, accountant, approver, support_agent=None) -> None:
    organization = ensure_organization(db, owner.id)
    ensure_membership(db, organization_id=organization.id, user_id=owner.id, role=MembershipRole.owner, title="Founder", can_invite_members=True)
    ensure_membership(db, organization_id=organization.id, user_id=accountant.id, role=MembershipRole.viewer, title="External Accountant")
    ensure_membership(db, organization_id=organization.id, user_id=approver.id, role=MembershipRole.approver, title="Operations Approver")
    ensure_approval_policy(db, organization_id=organization.id, user_id=owner.id)

    checking = ensure_account(db, owner.id, AccountCreate(name="Operating Checking", type=AccountType.bank, institution="BankOS Commercial", opening_balance=Decimal("8000"), organization_id=organization.id))
    tax_reserve = ensure_account(db, owner.id, AccountCreate(name="Tax Reserve", type=AccountType.bank, institution="BankOS Commercial", opening_balance=Decimal("12500"), organization_id=organization.id))
    rewards_card = ensure_account(db, owner.id, AccountCreate(name="Rewards Card", type=AccountType.credit_card, institution="BankOS Card Services", opening_balance=Decimal("1200"), interest_rate=Decimal("22.5"), organization_id=organization.id))
    equipment_loan = ensure_account(db, owner.id, AccountCreate(name="Equipment Loan", type=AccountType.loan, institution="BankOS Lending", opening_balance=Decimal("28000"), interest_rate=Decimal("8.25"), organization_id=organization.id))
    for account in [checking, tax_reserve, rewards_card, equipment_loan]:
        ensure_account_entitlement(db, organization_id=organization.id, account_id=account.id, user_id=owner.id, can_view=True, can_transact=True, can_approve=True)
        ensure_account_entitlement(db, organization_id=organization.id, account_id=account.id, user_id=accountant.id, can_view=True, can_transact=False, can_approve=False)
        ensure_account_entitlement(db, organization_id=organization.id, account_id=account.id, user_id=approver.id, can_view=True, can_transact=False, can_approve=True)
    ensure_transaction_set(db, owner.id, checking.id, [
        ("income", "Client Revenue", 12000, date(2026, 4, 1), "monthly"),
        ("expense", "Payroll", 4200, date(2026, 4, 3), "monthly"),
        ("expense", "Software", 480, date(2026, 4, 8), None),
        ("expense", "Marketing", 900, date(2026, 4, 12), None),
        ("expense", "Loan Payment", 700, date(2026, 4, 16), "monthly"),
    ])
    ensure_budgets(db, owner.id, [("Payroll", 5000), ("Software", 800), ("Marketing", 1200), ("Loan Payment", 900)])
    seed_business_payees_and_transfers(db, owner, organization, checking, tax_reserve)
    seed_business_card_activity(db, owner, support_agent, checking)
    for account in [checking, tax_reserve, rewards_card, equipment_loan]:
        snapshot_account_balance(db, account)
    generate_statement(db, owner, StatementGenerateRequest(account_id=checking.id, period_start=date(2026, 4, 1), period_end=date(2026, 4, 30)))
    db.commit()


def ensure_beneficiary(db, user, payload: BeneficiaryCreate) -> Beneficiary:
    beneficiary = db.scalar(
        select(Beneficiary).where(
            Beneficiary.owner_user_id == user.id,
            Beneficiary.organization_id == payload.organization_id,
            Beneficiary.display_name == payload.display_name,
        )
    )
    if beneficiary:
        return beneficiary
    return create_beneficiary(db, user, payload)


def ensure_transfer(db, user, payload: TransferCreate, *, submit: bool = True) -> Transfer:
    transfer = db.scalar(
        select(Transfer).where(
            Transfer.created_by_user_id == user.id,
            Transfer.from_account_id == payload.from_account_id,
            Transfer.amount == payload.amount,
            Transfer.memo == payload.memo,
        )
    )
    if transfer:
        ensure_transfer_controls(db, user, transfer)
        return transfer
    transfer = create_transfer(db, user, payload)
    if submit:
        transfer = submit_transfer(db, user, transfer.id)
    ensure_transfer_controls(db, user, transfer)
    return transfer


def ensure_transfer_controls(db, user, transfer: Transfer) -> None:
    if transfer.status == TransferStatus.posted:
        record_transfer_ledger_entries(db, transfer, actor_user_id=transfer.created_by_user_id)
        db.commit()
        return
    if transfer.status != TransferStatus.pending_approval:
        return
    risk_alerts = screen_transfer(db, transfer, user)
    required_approvals, separate_approver, reason = transfer_approval_requirement(
        db,
        transfer,
        requester_can_approve=True,
        force_approval=alerts_require_approval(risk_alerts),
    )
    if required_approvals < 1:
        required_approvals = 1
    ensure_transfer_approval_request(
        db,
        transfer,
        requested_by_user_id=transfer.created_by_user_id,
        required_approvals=required_approvals,
        require_separate_approver=separate_approver,
        reason=reason,
        metadata={"risk_alert_ids": [alert.id for alert in risk_alerts]},
    )
    create_hold_for_transfer(db, transfer, actor_user_id=transfer.created_by_user_id, reason=reason)
    db.commit()


def seed_business_payees_and_transfers(db, owner, organization: Organization, checking: Account, tax_reserve: Account) -> None:
    payroll = ensure_beneficiary(
        db,
        owner,
        BeneficiaryCreate(
            organization_id=organization.id,
            beneficiary_type=BeneficiaryType.external_ach,
            display_name="Payroll Provider",
            bank_name="First Payroll Bank",
            routing_number_last4="0110",
            account_number_last4="9021",
        ),
    )
    contractor = ensure_beneficiary(
        db,
        owner,
        BeneficiaryCreate(
            organization_id=organization.id,
            beneficiary_type=BeneficiaryType.wire,
            display_name="Expansion Contractor",
            bank_name="Continental Wire Bank",
            routing_number_last4="8765",
            account_number_last4="4412",
        ),
    )
    ensure_beneficiary(
        db,
        owner,
        BeneficiaryCreate(
            organization_id=organization.id,
            beneficiary_type=BeneficiaryType.bill_pay,
            display_name="City Tax Office",
            bank_name="Municipal Payments",
            routing_number_last4="1221",
            account_number_last4="4477",
        ),
    )
    ensure_beneficiary(
        db,
        owner,
        BeneficiaryCreate(
            organization_id=organization.id,
            beneficiary_type=BeneficiaryType.internal_account,
            display_name="Internal Tax Reserve",
            internal_account_id=tax_reserve.id,
        ),
    )
    ensure_transfer(
        db,
        owner,
        TransferCreate(
            organization_id=organization.id,
            from_account_id=checking.id,
            to_account_id=tax_reserve.id,
            transfer_type=TransferType.internal,
            amount=Decimal("750.00"),
            memo="Monthly reserve sweep",
        ),
    )
    ensure_transfer(
        db,
        owner,
        TransferCreate(
            organization_id=organization.id,
            from_account_id=checking.id,
            beneficiary_id=payroll.id,
            transfer_type=TransferType.external_ach,
            amount=Decimal("4200.00"),
            memo="April payroll funding",
        ),
    )
    ensure_transfer(
        db,
        owner,
        TransferCreate(
            organization_id=organization.id,
            from_account_id=checking.id,
            beneficiary_id=contractor.id,
            transfer_type=TransferType.wire,
            amount=Decimal("5500.00"),
            memo="Studio expansion deposit",
        ),
    )


def seed_personal_card_activity(db, user: User, checking: Account) -> None:
    card = ensure_card(
        db,
        user,
        checking,
        display_name="Everyday Debit Card",
        daily_limit=Decimal("800.00"),
        monthly_limit=Decimal("3500.00"),
        blocked_merchant_categories="Gambling",
    )
    ensure_card_authorization(
        db,
        user,
        card,
        amount=Decimal("76.42"),
        merchant_name="Lakeview Market",
        merchant_category="Groceries",
    )


def seed_personal_banking(db, user_id: int, readonly: bool = False) -> None:
    checking = ensure_account(db, user_id, AccountCreate(name="Everyday Checking", type=AccountType.bank, institution="BankOS Retail", opening_balance=Decimal("4200")))
    ensure_account(db, user_id, AccountCreate(name="Emergency Savings", type=AccountType.bank, institution="BankOS Retail", opening_balance=Decimal("18500")))
    ensure_account(db, user_id, AccountCreate(name="Cash Wallet", type=AccountType.cash, opening_balance=Decimal("250")))
    ensure_account(db, user_id, AccountCreate(name="Travel Card", type=AccountType.credit_card, institution="BankOS Card Services", opening_balance=Decimal("860"), interest_rate=Decimal("19.99")))
    ensure_account(db, user_id, AccountCreate(name="Student Loan", type=AccountType.loan, institution="BankOS Lending", opening_balance=Decimal("14500"), interest_rate=Decimal("5.75")))
    ensure_transaction_set(db, user_id, checking.id, [
        ("income", "Salary", 8200, date(2026, 4, 1), "biweekly"),
        ("expense", "Rent", 2200, date(2026, 4, 2), "monthly"),
        ("expense", "Groceries", 620, date(2026, 4, 7), None),
        ("expense", "Utilities", 240, date(2026, 4, 10), "monthly"),
        ("expense", "Student Loan", 410, date(2026, 4, 15), "monthly"),
        ("expense", "Travel", 520 if not readonly else 180, date(2026, 4, 18), None),
    ])
    ensure_budgets(db, user_id, [("Rent", 2300), ("Groceries", 800), ("Utilities", 350), ("Travel", 650), ("Student Loan", 500)])
    user = db.get(User, user_id)
    if user:
        if not readonly:
            seed_personal_card_activity(db, user, checking)
        snapshot_account_balance(db, checking)
        generate_statement(db, user, StatementGenerateRequest(account_id=checking.id, period_start=date(2026, 4, 1), period_end=date(2026, 4, 30)))
        db.commit()


def seed_accountant_view(db, user_id: int) -> None:
    checking = ensure_account(db, user_id, AccountCreate(name="Client Trust Review", type=AccountType.bank, institution="BankOS Commercial", opening_balance=Decimal("3500")))
    ensure_transaction_set(db, user_id, checking.id, [
        ("income", "Accounting Retainer", 3500, date(2026, 4, 1), "monthly"),
        ("expense", "Professional Tools", 260, date(2026, 4, 6), "monthly"),
        ("expense", "Continuing Education", 400, date(2026, 4, 20), None),
    ])
    ensure_budgets(db, user_id, [("Professional Tools", 300), ("Continuing Education", 600)])


def run() -> None:
    ensure_sqlite_development_schema(engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        bootstrap_iam(db)
        users_by_email = {}
        for spec in DEMO_USERS:
            user = ensure_user(db, spec)
            users_by_email[spec["email"]] = user
        seed_business_banking(
            db,
            users_by_email["owner@acme.com"],
            users_by_email["accountant@acme.com"],
            users_by_email["approver@acme.com"],
            users_by_email["support@bankos.com"],
        )
        for spec in DEMO_USERS:
            user = users_by_email[spec["email"]]
            banking = spec.get("banking")
            if banking == "accountant":
                seed_accountant_view(db, user.id)
            elif banking in {"personal", "personal_readonly"}:
                seed_personal_banking(db, user.id, readonly=banking == "personal_readonly")
    finally:
        db.close()


if __name__ == "__main__":
    run()
