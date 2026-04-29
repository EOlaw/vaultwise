import os
from datetime import date, timedelta
from uuid import uuid4

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.accounts.models import Account
from app.approvals.models import ApprovalDecision, ApprovalPolicy, ApprovalRequest
from app.audit.models import AuditLog, SecurityEvent
from app.auth.mfa import totp_code
from app.auth.models import IdempotencyKey, LoginAttempt, MultiFactorDevice, RefreshToken, UserSession
from app.budgets.models import Budget
from app.cards.models import Card, CardAuthorization, CardControl
from app.database import Base, SessionLocal, engine
from app.disputes.models import Dispute, DisputeEvent
from app.iam.models import PolicyDecision, UserRoleAssignment
from app.iam.service import assign_role, bootstrap_iam
from app.ledger.models import AccountBalanceSnapshot, AccountHold, LedgerEntry
from app.app import app
from app.notifications.models import Notification
from app.organizations.models import AccountEntitlement, Organization, OrganizationMembership
from app.risk.models import ComplianceCase, RiskAlert
from app.statements.models import AccountStatement, AccountStatementLine
from app.transactions.models import Transaction
from app.transfers.models import Beneficiary, Transfer, TransferEvent
from app.transfers.service import post_due_scheduled_transfers
from app.users.models import CustomerType, KycStatus, RiskRating, User, UserProfile, UserRole
from app.users.schemas import UserCreate
from app.users.service import create_user
from app.utils.dev_migrations import ensure_sqlite_development_schema


ensure_sqlite_development_schema(engine)
Base.metadata.create_all(bind=engine)


def _create_user(role_name: str) -> tuple[int, str, str]:
    email = f"{role_name}-{uuid4().hex[:10]}@example.com"
    password = "password123"
    db = SessionLocal()
    try:
        bootstrap_iam(db)
        user = create_user(db, UserCreate(email=email, full_name=role_name.replace("_", " ").title(), password=password, role=UserRole.user))
        db.add(
            UserProfile(
                user_id=user.id,
                customer_reference=f"TST-{uuid4().hex[:10].upper()}",
                customer_type=CustomerType.business,
                kyc_status=KycStatus.verified,
                risk_rating=RiskRating.low,
                country="United States",
            )
        )
        db.commit()
        assign_role(db, user_id=user.id, role_name=role_name)
        return user.id, email, password
    finally:
        db.close()


def _auth_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _step_up(client: TestClient, headers: dict[str, str], password: str = "password123", mfa_code: str | None = None) -> None:
    payload = {"mfa_code": mfa_code} if mfa_code else {"password": password}
    response = client.post("/auth/step-up", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json()["step_up_expires_at"]


def _cleanup_test_data(*, legal_name: str, emails: list[str]) -> None:
    db = SessionLocal()
    try:
        org_ids = list(db.scalars(select(Organization.id).where(Organization.legal_name == legal_name)).all())
        user_ids = list(db.scalars(select(User.id).where(User.email.in_(emails))).all())
        account_ids = list(db.scalars(select(Account.id).where(Account.organization_id.in_(org_ids))).all()) if org_ids else []
        transfer_ids = list(db.scalars(select(Transfer.id).where(Transfer.organization_id.in_(org_ids))).all()) if org_ids else []
        session_ids = list(db.scalars(select(UserSession.id).where(UserSession.user_id.in_(user_ids))).all()) if user_ids else []

        if transfer_ids:
            approval_ids = list(db.scalars(select(ApprovalRequest.id).where(ApprovalRequest.transfer_id.in_(transfer_ids))).all())
            alert_ids = list(db.scalars(select(RiskAlert.id).where(RiskAlert.transfer_id.in_(transfer_ids))).all())
            if approval_ids:
                db.execute(delete(ApprovalDecision).where(ApprovalDecision.approval_request_id.in_(approval_ids)))
                db.execute(delete(ApprovalRequest).where(ApprovalRequest.id.in_(approval_ids)))
            if alert_ids:
                db.execute(delete(ComplianceCase).where(ComplianceCase.alert_id.in_(alert_ids)))
                db.execute(delete(RiskAlert).where(RiskAlert.id.in_(alert_ids)))
            db.execute(delete(AccountHold).where(AccountHold.transfer_id.in_(transfer_ids)))
            db.execute(delete(LedgerEntry).where(LedgerEntry.transfer_id.in_(transfer_ids)))
            db.execute(delete(TransferEvent).where(TransferEvent.transfer_id.in_(transfer_ids)))
        if org_ids:
            db.execute(delete(ApprovalPolicy).where(ApprovalPolicy.organization_id.in_(org_ids)))
            statement_ids = list(db.scalars(select(AccountStatement.id).where(AccountStatement.organization_id.in_(org_ids))).all())
            if statement_ids:
                db.execute(delete(AccountStatementLine).where(AccountStatementLine.statement_id.in_(statement_ids)))
                db.execute(delete(AccountStatement).where(AccountStatement.id.in_(statement_ids)))
            db.execute(delete(Notification).where(Notification.organization_id.in_(org_ids)))
            db.execute(delete(Transfer).where(Transfer.organization_id.in_(org_ids)))
            db.execute(delete(Beneficiary).where(Beneficiary.organization_id.in_(org_ids)))
            db.execute(delete(AccountEntitlement).where(AccountEntitlement.organization_id.in_(org_ids)))
            db.execute(delete(OrganizationMembership).where(OrganizationMembership.organization_id.in_(org_ids)))
        if account_ids:
            auth_ids = list(db.scalars(select(CardAuthorization.id).where(CardAuthorization.account_id.in_(account_ids))).all())
            dispute_ids = list(db.scalars(select(Dispute.id).where(Dispute.account_id.in_(account_ids))).all())
            if dispute_ids:
                db.execute(delete(DisputeEvent).where(DisputeEvent.dispute_id.in_(dispute_ids)))
                db.execute(delete(Dispute).where(Dispute.id.in_(dispute_ids)))
            if auth_ids:
                db.execute(delete(AccountHold).where(AccountHold.card_authorization_id.in_(auth_ids)))
                db.execute(delete(CardAuthorization).where(CardAuthorization.id.in_(auth_ids)))
            card_ids = list(db.scalars(select(Card.id).where(Card.account_id.in_(account_ids))).all())
            if card_ids:
                db.execute(delete(CardControl).where(CardControl.card_id.in_(card_ids)))
                db.execute(delete(Card).where(Card.id.in_(card_ids)))
            db.execute(delete(AccountBalanceSnapshot).where(AccountBalanceSnapshot.account_id.in_(account_ids)))
            db.execute(delete(AccountHold).where(AccountHold.account_id.in_(account_ids)))
            db.execute(delete(LedgerEntry).where(LedgerEntry.account_id.in_(account_ids)))
            db.execute(delete(Transaction).where(Transaction.account_id.in_(account_ids)))
            db.execute(delete(Account).where(Account.id.in_(account_ids)))
        if org_ids:
            db.execute(delete(Organization).where(Organization.id.in_(org_ids)))
        if user_ids:
            db.execute(delete(IdempotencyKey).where(IdempotencyKey.user_id.in_(user_ids)))
            db.execute(delete(MultiFactorDevice).where(MultiFactorDevice.user_id.in_(user_ids)))
            if session_ids:
                db.execute(delete(RefreshToken).where(RefreshToken.session_id.in_(session_ids)))
            db.execute(delete(LoginAttempt).where(LoginAttempt.user_id.in_(user_ids)))
            db.execute(delete(UserSession).where(UserSession.user_id.in_(user_ids)))
            db.execute(delete(Budget).where(Budget.user_id.in_(user_ids)))
            db.execute(delete(Transaction).where(Transaction.user_id.in_(user_ids)))
            db.execute(delete(Account).where(Account.user_id.in_(user_ids)))
            db.execute(delete(UserRoleAssignment).where(UserRoleAssignment.user_id.in_(user_ids)))
            db.execute(delete(PolicyDecision).where(PolicyDecision.user_id.in_(user_ids)))
            db.execute(delete(AuditLog).where(AuditLog.actor_user_id.in_(user_ids)))
            db.execute(delete(SecurityEvent).where(SecurityEvent.user_id.in_(user_ids)))
            db.execute(delete(Notification).where(Notification.user_id.in_(user_ids)))
            db.execute(delete(UserProfile).where(UserProfile.user_id.in_(user_ids)))
            db.execute(delete(User).where(User.id.in_(user_ids)))
        db.commit()
    finally:
        db.close()


def test_business_owner_money_movement_and_accountant_abac():
    client = TestClient(app)
    owner_id, owner_email, owner_password = _create_user("business_owner")
    accountant_id, accountant_email, accountant_password = _create_user("accountant")
    owner_headers = _auth_headers(client, owner_email, owner_password)
    _step_up(client, owner_headers, owner_password)
    legal_name = f"Phase Test Co {owner_id} LLC"

    try:
        organization_response = client.post(
            "/organizations",
            headers=owner_headers,
            json={
                "name": "Phase Test Co",
                "legal_name": legal_name,
                "organization_type": "business",
                "tax_id_last4": "1234",
                "country": "United States",
            },
        )
        assert organization_response.status_code == 201
        organization_id = organization_response.json()["id"]

        account_response = client.post(
            "/accounts",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "name": "Operating Account",
                "type": "bank",
                "institution": "BankOS Commercial",
                "opening_balance": "1000.00",
                "interest_rate": "0",
            },
        )
        assert account_response.status_code == 201
        account_id = account_response.json()["id"]

        membership_response = client.post(
            f"/organizations/{organization_id}/memberships",
            headers=owner_headers,
            json={"user_id": accountant_id, "role": "viewer", "title": "Bookkeeper"},
        )
        assert membership_response.status_code == 201

        entitlement_response = client.post(
            f"/organizations/{organization_id}/entitlements",
            headers=owner_headers,
            json={"account_id": account_id, "user_id": accountant_id, "can_view": True, "can_transact": False, "can_approve": False},
        )
        assert entitlement_response.status_code == 201

        beneficiary_response = client.post(
            "/beneficiaries",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "beneficiary_type": "external_ach",
                "display_name": "Vendor ACH",
                "bank_name": "Vendor Bank",
                "routing_number_last4": "1111",
                "account_number_last4": "2222",
            },
        )
        assert beneficiary_response.status_code == 201
        beneficiary_id = beneficiary_response.json()["id"]

        transfer_response = client.post(
            "/transfers",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "from_account_id": account_id,
                "beneficiary_id": beneficiary_id,
                "transfer_type": "external_ach",
                "amount": "25.00",
                "memo": "Vendor test payment",
            },
        )
        assert transfer_response.status_code == 201
        transfer_id = transfer_response.json()["id"]

        submit_headers = {**owner_headers, "Idempotency-Key": f"submit-{transfer_id}-{uuid4().hex}"}
        submit_response = client.post(f"/transfers/{transfer_id}/submit", headers=submit_headers)
        assert submit_response.status_code == 200
        assert submit_response.json()["status"] == "posted"

        replay_submit = client.post(f"/transfers/{transfer_id}/submit", headers=submit_headers)
        assert replay_submit.status_code == 200
        assert replay_submit.json()["id"] == transfer_id

        accountant_headers = _auth_headers(client, accountant_email, accountant_password)
        accounts_response = client.get("/accounts", headers=accountant_headers)
        assert accounts_response.status_code == 200
        assert any(account["id"] == account_id for account in accounts_response.json())

        denied_transfer = client.post(
            "/transfers",
            headers=accountant_headers,
            json={
                "organization_id": organization_id,
                "from_account_id": account_id,
                "beneficiary_id": beneficiary_id,
                "transfer_type": "external_ach",
                "amount": "25.00",
            },
        )
        assert denied_transfer.status_code == 403
    finally:
        _cleanup_test_data(legal_name=legal_name, emails=[owner_email, accountant_email])


def test_approval_policy_and_risk_alert_workflow():
    client = TestClient(app)
    owner_id, owner_email, owner_password = _create_user("business_owner")
    approver_id, approver_email, approver_password = _create_user("business_admin")
    _, risk_email, risk_password = _create_user("risk_manager")
    owner_headers = _auth_headers(client, owner_email, owner_password)
    _step_up(client, owner_headers, owner_password)
    legal_name = f"Phase Controls Co {owner_id} LLC"

    try:
        organization_response = client.post(
            "/organizations",
            headers=owner_headers,
            json={
                "name": "Phase Controls Co",
                "legal_name": legal_name,
                "organization_type": "business",
                "tax_id_last4": "9988",
                "country": "United States",
            },
        )
        assert organization_response.status_code == 201
        organization_id = organization_response.json()["id"]

        account_response = client.post(
            "/accounts",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "name": "Control Operating",
                "type": "bank",
                "institution": "BankOS Commercial",
                "opening_balance": "5000.00",
                "interest_rate": "0",
            },
        )
        assert account_response.status_code == 201
        account_id = account_response.json()["id"]

        assert client.post(
            f"/organizations/{organization_id}/memberships",
            headers=owner_headers,
            json={"user_id": approver_id, "role": "approver", "title": "Dual Control Approver"},
        ).status_code == 201
        assert client.post(
            f"/organizations/{organization_id}/entitlements",
            headers=owner_headers,
            json={"account_id": account_id, "user_id": approver_id, "can_view": True, "can_transact": False, "can_approve": True},
        ).status_code == 201

        policy_response = client.post(
            "/approvals/policies",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "name": "Test dual-control threshold",
                "min_amount": "100.00",
                "required_approvals": 1,
                "require_separate_approver": True,
            },
        )
        assert policy_response.status_code == 201

        beneficiary_response = client.post(
            "/beneficiaries",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "beneficiary_type": "external_ach",
                "display_name": "Controls Vendor",
                "bank_name": "Vendor Bank",
                "routing_number_last4": "1111",
                "account_number_last4": "3333",
            },
        )
        assert beneficiary_response.status_code == 201
        beneficiary_id = beneficiary_response.json()["id"]

        transfer_response = client.post(
            "/transfers",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "from_account_id": account_id,
                "beneficiary_id": beneficiary_id,
                "transfer_type": "external_ach",
                "amount": "1500.00",
                "memo": "Policy controlled payment",
            },
        )
        assert transfer_response.status_code == 201
        transfer_id = transfer_response.json()["id"]

        submit_response = client.post(f"/transfers/{transfer_id}/submit", headers=owner_headers)
        assert submit_response.status_code == 200
        assert submit_response.json()["status"] == "pending_approval"

        holds_response = client.get(f"/ledger/holds?account_id={account_id}&status_filter=active", headers=owner_headers)
        assert holds_response.status_code == 200
        assert any(hold["transfer_id"] == transfer_id for hold in holds_response.json())

        balance_response = client.get(f"/ledger/accounts/{account_id}/balance", headers=owner_headers)
        assert balance_response.status_code == 200
        assert balance_response.json()["held_amount"] == "1500.00"

        approvals_response = client.get("/approvals", headers=owner_headers)
        assert approvals_response.status_code == 200
        approval = next(row for row in approvals_response.json() if row["transfer_id"] == transfer_id)
        assert approval["status"] == "pending"

        approver_headers = _auth_headers(client, approver_email, approver_password)
        _step_up(client, approver_headers, approver_password)
        approve_response = client.post(f"/approvals/{approval['id']}/approve", headers=approver_headers, json={"notes": "Approved in test"})
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"

        posted_transfer = client.get(f"/transfers/{transfer_id}", headers=owner_headers)
        assert posted_transfer.status_code == 200
        assert posted_transfer.json()["status"] == "posted"

        released_holds = client.get(f"/ledger/holds?account_id={account_id}", headers=owner_headers)
        assert released_holds.status_code == 200
        assert any(hold["transfer_id"] == transfer_id and hold["status"] == "released" for hold in released_holds.json())

        ledger_response = client.get(f"/ledger/accounts/{account_id}/entries", headers=owner_headers)
        assert ledger_response.status_code == 200
        assert any(entry["transfer_id"] == transfer_id and entry["direction"] == "debit" for entry in ledger_response.json())

        statement_response = client.post(
            "/statements/generate",
            headers=owner_headers,
            json={"account_id": account_id, "period_start": "2026-04-01", "period_end": "2026-04-30"},
        )
        assert statement_response.status_code == 201
        assert statement_response.json()["account_id"] == account_id

        notifications_response = client.get("/notifications", headers=owner_headers)
        assert notifications_response.status_code == 200
        assert any(notification["notification_type"] in {"transfer", "statement"} for notification in notifications_response.json())

        risk_headers = _auth_headers(client, risk_email, risk_password)
        alerts_response = client.get("/risk/alerts", headers=risk_headers)
        assert alerts_response.status_code == 200
        assert any(alert["transfer_id"] == transfer_id for alert in alerts_response.json())
    finally:
        _cleanup_test_data(legal_name=legal_name, emails=[owner_email, approver_email, risk_email])


def test_card_authorization_capture_and_dispute_workflow():
    client = TestClient(app)
    owner_id, owner_email, owner_password = _create_user("business_owner")
    _, support_email, support_password = _create_user("support_agent")
    owner_headers = _auth_headers(client, owner_email, owner_password)
    _step_up(client, owner_headers, owner_password)
    legal_name = f"Phase Cards Co {owner_id} LLC"

    try:
        organization_response = client.post(
            "/organizations",
            headers=owner_headers,
            json={
                "name": "Phase Cards Co",
                "legal_name": legal_name,
                "organization_type": "business",
                "tax_id_last4": "4411",
                "country": "United States",
            },
        )
        assert organization_response.status_code == 201
        organization_id = organization_response.json()["id"]

        account_response = client.post(
            "/accounts",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "name": "Card Operating",
                "type": "bank",
                "institution": "BankOS Commercial",
                "opening_balance": "1200.00",
                "interest_rate": "0",
            },
        )
        assert account_response.status_code == 201
        account_id = account_response.json()["id"]

        card_response = client.post(
            "/cards",
            headers=owner_headers,
            json={
                "account_id": account_id,
                "display_name": "Operations Card",
                "card_type": "debit",
                "network": "visa",
                "daily_limit": "500.00",
                "monthly_limit": "2500.00",
            },
        )
        assert card_response.status_code == 201
        card_id = card_response.json()["id"]

        savings_card_response = client.post(
            "/cards",
            headers=owner_headers,
            json={
                "account_id": account_id,
                "display_name": "Savings Access Card",
                "card_type": "savings",
                "network": "mastercard",
                "daily_limit": "200.00",
                "monthly_limit": "1000.00",
            },
        )
        assert savings_card_response.status_code == 201
        assert savings_card_response.json()["controls"]["allow_online"] is False
        assert savings_card_response.json()["controls"]["require_pin"] is True

        off_response = client.post(f"/cards/{card_id}/turn-off", headers=owner_headers)
        assert off_response.status_code == 200
        assert off_response.json()["status"] == "frozen"

        frozen_decline = client.post(
            "/cards/authorizations",
            headers=owner_headers,
            json={
                "card_id": card_id,
                "amount": "15.00",
                "merchant_name": "Office Cafe",
                "merchant_category": "Food",
                "channel": "card_present",
            },
        )
        assert frozen_decline.status_code == 201
        assert frozen_decline.json()["status"] == "declined"
        assert frozen_decline.json()["decline_reason"] == "Card is not active"

        on_response = client.post(f"/cards/{card_id}/turn-on", headers=owner_headers)
        assert on_response.status_code == 200
        assert on_response.json()["status"] == "active"

        blocked_update = client.patch(
            f"/cards/{card_id}/controls",
            headers=owner_headers,
            json={"blocked_merchant_categories": "Gambling", "allow_contactless": False, "max_transaction_amount": "100.00"},
        )
        assert blocked_update.status_code == 200
        assert blocked_update.json()["allow_contactless"] is False

        channel_decline = client.post(
            "/cards/authorizations",
            headers=owner_headers,
            json={
                "card_id": card_id,
                "amount": "25.00",
                "merchant_name": "Tap Terminal",
                "merchant_category": "Office Supplies",
                "channel": "contactless",
            },
        )
        assert channel_decline.status_code == 201
        assert channel_decline.json()["status"] == "declined"
        assert channel_decline.json()["decline_reason"] == "Contactless transactions are disabled"

        amount_decline = client.post(
            "/cards/authorizations",
            headers=owner_headers,
            json={
                "card_id": card_id,
                "amount": "125.00",
                "merchant_name": "Office Warehouse",
                "merchant_category": "Office Supplies",
                "channel": "card_present",
            },
        )
        assert amount_decline.status_code == 201
        assert amount_decline.json()["status"] == "declined"
        assert amount_decline.json()["decline_reason"] == "Card transaction limit exceeded"

        decline_response = client.post(
            "/cards/authorizations",
            headers=owner_headers,
            json={
                "card_id": card_id,
                "amount": "25.00",
                "merchant_name": "City Casino",
                "merchant_category": "Gambling",
                "card_not_present": True,
            },
        )
        assert decline_response.status_code == 201
        assert decline_response.json()["status"] == "declined"

        auth_response = client.post(
            "/cards/authorizations",
            headers=owner_headers,
            json={
                "card_id": card_id,
                "amount": "80.00",
                "merchant_name": "Office Depot",
                "merchant_category": "Office Supplies",
                "card_not_present": True,
                "channel": "online",
            },
        )
        assert auth_response.status_code == 201
        assert auth_response.json()["status"] == "approved"
        authorization_id = auth_response.json()["id"]

        holds_response = client.get(f"/ledger/holds?account_id={account_id}&status_filter=active", headers=owner_headers)
        assert holds_response.status_code == 200
        assert any(hold["card_authorization_id"] == authorization_id for hold in holds_response.json())

        capture_headers = {**owner_headers, "Idempotency-Key": f"capture-{authorization_id}-{uuid4().hex}"}
        capture_response = client.post(f"/cards/authorizations/{authorization_id}/capture", headers=capture_headers)
        assert capture_response.status_code == 200
        assert capture_response.json()["status"] == "captured"
        transaction_id = capture_response.json()["transaction_id"]

        replay_capture = client.post(f"/cards/authorizations/{authorization_id}/capture", headers=capture_headers)
        assert replay_capture.status_code == 200
        assert replay_capture.json()["transaction_id"] == transaction_id

        ledger_response = client.get(f"/ledger/accounts/{account_id}/entries", headers=owner_headers)
        assert ledger_response.status_code == 200
        assert any(entry["transaction_id"] == transaction_id and entry["direction"] == "debit" for entry in ledger_response.json())

        dispute_response = client.post(
            "/disputes",
            headers=owner_headers,
            json={
                "card_authorization_id": authorization_id,
                "reason": "incorrect_amount",
                "amount": "80.00",
                "description": "Merchant charged the wrong amount for office supplies.",
            },
        )
        assert dispute_response.status_code == 201
        dispute_id = dispute_response.json()["id"]

        support_headers = _auth_headers(client, support_email, support_password)
        _step_up(client, support_headers, support_password)
        provisional_response = client.patch(
            f"/disputes/{dispute_id}/status",
            headers=support_headers,
            json={"status": "provisional_credit", "notes": "Credit issued while evidence is reviewed."},
        )
        assert provisional_response.status_code == 200
        assert provisional_response.json()["status"] == "provisional_credit"
        assert provisional_response.json()["provisional_transaction_id"] is not None
    finally:
        _cleanup_test_data(legal_name=legal_name, emails=[owner_email, support_email])


def test_mfa_login_step_up_and_trusted_device_workflow():
    client = TestClient(app)
    user_id, email, password = _create_user("customer")
    headers = _auth_headers(client, email, password)
    legal_name = f"Security Phase No Org {user_id}"

    try:
        setup_response = client.post("/auth/mfa/setup", headers=headers, json={"label": "Test authenticator"})
        assert setup_response.status_code == 201
        setup_payload = setup_response.json()
        secret = setup_payload["secret"]

        confirm_response = client.post(
            f"/auth/mfa/{setup_payload['device_id']}/confirm",
            headers=headers,
            json={"code": totp_code(secret)},
        )
        assert confirm_response.status_code == 200
        assert confirm_response.json()["is_confirmed"] is True

        missing_mfa_login = client.post("/auth/login", json={"email": email, "password": password})
        assert missing_mfa_login.status_code == 401

        mfa_login = client.post(
            "/auth/login",
            headers={"X-Device-Fingerprint": "phase-9-test-device", "X-Device-Label": "Phase 9 Test Browser"},
            json={"email": email, "password": password, "mfa_code": totp_code(secret)},
        )
        assert mfa_login.status_code == 200
        mfa_headers = {"Authorization": f"Bearer {mfa_login.json()['access_token']}"}

        trust_response = client.post("/auth/sessions/current/trust", headers=mfa_headers)
        assert trust_response.status_code == 200
        assert trust_response.json()["trusted_device"] is True

        step_up_response = client.post("/auth/step-up", headers=mfa_headers, json={"mfa_code": totp_code(secret)})
        assert step_up_response.status_code == 200
        assert step_up_response.json()["step_up_expires_at"]
    finally:
        _cleanup_test_data(legal_name=legal_name, emails=[email])


def test_scheduled_transfer_processing_reconciliation_and_pdf_export():
    client = TestClient(app)
    owner_id, owner_email, owner_password = _create_user("business_owner")
    owner_headers = _auth_headers(client, owner_email, owner_password)
    _step_up(client, owner_headers, owner_password)
    legal_name = f"Operations Test Co {owner_id} LLC"

    try:
        organization_response = client.post(
            "/organizations",
            headers=owner_headers,
            json={
                "name": "Operations Test Co",
                "legal_name": legal_name,
                "organization_type": "business",
                "tax_id_last4": "4321",
                "country": "United States",
            },
        )
        assert organization_response.status_code == 201
        organization_id = organization_response.json()["id"]

        account_response = client.post(
            "/accounts",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "name": "Treasury Operating",
                "type": "bank",
                "institution": "BankOS Commercial",
                "opening_balance": "1000.00",
                "interest_rate": "0",
            },
        )
        assert account_response.status_code == 201
        account_id = account_response.json()["id"]

        beneficiary_response = client.post(
            "/beneficiaries",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "beneficiary_type": "external_ach",
                "display_name": "Scheduled Vendor",
                "bank_name": "Vendor Bank",
                "routing_number_last4": "1111",
                "account_number_last4": "2222",
            },
        )
        assert beneficiary_response.status_code == 201
        beneficiary_id = beneficiary_response.json()["id"]

        scheduled_for = date.today() + timedelta(days=1)
        transfer_response = client.post(
            "/transfers",
            headers=owner_headers,
            json={
                "organization_id": organization_id,
                "from_account_id": account_id,
                "beneficiary_id": beneficiary_id,
                "transfer_type": "external_ach",
                "amount": "25.00",
                "memo": "Scheduled vendor payment",
                "scheduled_for": scheduled_for.isoformat(),
            },
        )
        assert transfer_response.status_code == 201
        transfer_id = transfer_response.json()["id"]

        submit_response = client.post(f"/transfers/{transfer_id}/submit", headers={**owner_headers, "Idempotency-Key": f"submit-{transfer_id}-{uuid4().hex}"})
        assert submit_response.status_code == 200
        assert submit_response.json()["status"] == "scheduled"

        db = SessionLocal()
        try:
            result = post_due_scheduled_transfers(db, as_of=scheduled_for)
            assert result["posted_ids"] == [transfer_id]
        finally:
            db.close()

        reconciliation_response = client.get(f"/ledger/reconciliation?account_id={account_id}", headers=owner_headers)
        assert reconciliation_response.status_code == 200
        reconciliation = reconciliation_response.json()
        assert reconciliation["status"] == "ok"
        assert reconciliation["accounts"][0]["variance"] == "0.00"

        pdf_response = client.get("/reports/export.pdf", headers=owner_headers)
        assert pdf_response.status_code == 200
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert pdf_response.content.startswith(b"%PDF-1.4")
    finally:
        _cleanup_test_data(legal_name=legal_name, emails=[owner_email])
