# Architecture

BankOS is organized as a modular banking platform. The backend owns authentication, authorization, business rules, persistence, and banking workflows. The frontend consumes the API and presents customer, business, and operations pages.

## Runtime Components

- `servers/app/app.py`: FastAPI application factory point, middleware, startup bootstrap, health check, and router registration.
- `servers/server.py`: Uvicorn entrypoint used by the backend Docker image.
- `servers/app/database.py`: SQLAlchemy engine, session factory, and declarative base.
- `servers/app/config.py`: Pydantic settings loaded from environment variables or `servers/.env`.
- `src/app/*`: Next.js page routes for banking, admin, risk, reporting, cards, approvals, and other product surfaces.
- `src/api/*`: frontend API clients grouped by role or domain.
- `docker-compose.yml`: PostgreSQL, Redis, backend, and frontend local composition.

## Backend Module Pattern

Most backend domains follow the same shape:

- `models.py`: SQLAlchemy tables and enums.
- `schemas.py`: Pydantic request and response contracts.
- `routes.py`: FastAPI endpoints, dependency wiring, and HTTP concerns.
- `service.py`: business rules, ownership checks, state transitions, calculations, and database writes.

This keeps route handlers thin and makes the service layer easier to test directly.

## Domain Modules

- `auth`: registration, login, refresh-token rotation, logout, sessions, MFA setup/confirmation, trusted devices, and step-up authentication.
- `iam`: permissions, roles, assignments, policy decisions, and bootstrap defaults.
- `users`: user records, profile metadata, KYC/risk fields, and admin user updates.
- `accounts`: cash, bank, credit card, investment, and loan accounts.
- `transactions`: income, expense, transfer records, tags, notes, receipts, and recurring rules.
- `budgets`: monthly category limits and computed progress.
- `dashboard`: aggregate financial dashboard data from accounts, transactions, and budgets.
- `reports`: monthly/yearly/category summaries and CSV export.
- `analytics`: financial summary, loan payoff, and investment growth calculations.
- `organizations`: business profiles, memberships, and account entitlements.
- `transfers`: beneficiaries/payees, transfer drafts, submission, cancellation, approval handoff, and posting support.
- `approvals`: approval policies, approval requests, approve/reject decisions, and dual-control enforcement.
- `risk`: transfer risk alerts and compliance cases.
- `ledger`: available balances, account holds, ledger entries, reconciliation, and snapshots.
- `statements`: generated account statements and statement lines.
- `notifications`: banking notifications and read tracking.
- `cards`: issued cards, controls, freezes, closures, authorizations, captures, and reversals.
- `disputes`: transaction/card disputes, lifecycle events, provisional credits, and support workflows.
- `audit`: audit/security event models and logging support.
- `calculations`: standalone finance formula modules.
- `tasks`: Celery task placeholders for async reports, scheduled transfer posting, and hold expiration.

## Security Model

BankOS uses layered controls:

- JWT access tokens authenticate API requests.
- Refresh tokens rotate through `/auth/refresh`.
- User sessions are tracked with a `sid` claim and can be revoked.
- Optional TOTP MFA can be enrolled, confirmed, and required at login.
- Step-up authentication creates a short recent-auth window for sensitive operations.
- Trusted devices are tracked on sessions after step-up.
- IAM roles map users to permissions such as `transfers:create`, `cards:manage`, and `audit:read`.
- Route dependencies enforce permissions through `require_permission(...)`.
- Business banking access also checks organization membership and account entitlements.

The seed data includes personas that intentionally exercise different permission levels.

## Sensitive Operation Controls

Certain workflows require more than a valid access token:

- Payee/beneficiary creation or update.
- Transfer creation, submission, approval, or cancellation.
- Approval decisions and approval policy management.
- Card issuance, controls, freezes, closures, authorizations, captures, and reversals.
- Managed dispute status changes.
- MFA device removal and trusted-device updates.

For these requests, call `/auth/step-up` first with the user's password and then retry the sensitive request before the step-up window expires.

Retryable transfer operations, approval decisions, card authorizations/captures/reversals, and dispute status changes also accept `Idempotency-Key` so a client can safely retry without creating duplicate side effects.

## Business Banking Flow

1. A business owner creates or uses an organization.
2. Members are added with business roles such as owner, viewer, or approver.
3. Accounts are attached to the organization.
4. Entitlements decide which users can view, transact, or approve against each account.
5. Beneficiaries/payees are created for internal accounts, ACH, wires, or bill pay.
6. Transfers are created as drafts and submitted.
7. The transfer service screens for risk and evaluates approval policies.
8. Pending transfers create approval requests and ledger holds.
9. An eligible approver approves or rejects.
10. Approved transfers can be posted and reflected in ledger entries, balances, notifications, and statements.

## Card And Dispute Flow

1. A card is issued against an account.
2. Controls determine online, card-present, contactless, international, ATM, PIN, amount, and merchant-category rules.
3. Authorization requests are approved or declined based on card status, controls, limits, and balance checks.
4. Approved authorizations create holds.
5. Capture converts the authorization to a posted transaction and ledger effect.
6. Reversal releases an eligible authorization.
7. A customer can open a dispute against a transaction or card authorization.
8. Support or operations users can advance the dispute lifecycle and grant provisional credit where appropriate.

## Ledger Model

The ledger module separates balance-facing operations from account records:

- Account balances show current and available positions.
- Holds reserve funds for transfer/card activity.
- Ledger entries represent durable posting activity.
- Snapshots record account balance state for statements and reconciliation.
- Reconciliation summarizes balance, hold, and ledger consistency.

This design lets money movement, cards, disputes, and statements use the same accounting primitives.

## Data And Migrations

Production is designed for PostgreSQL and Alembic migrations in `servers/alembic/versions`.

Development can use SQLite with `DATABASE_URL=sqlite:///./finance.db`. In `ENVIRONMENT=development`, startup runs helper migrations and `Base.metadata.create_all(...)` to make local testing fast. This is convenient for demos, but production deployments should apply Alembic migrations explicitly.

## Seed Data

`servers/app/utils/seed.py` creates:

- Internal users for admin, bank admin, compliance, risk, and support.
- Acme business users for owner, accountant, and approver.
- Personal users for customer and read-only testing.
- Profiles with KYC/risk metadata.
- Acme organization, memberships, accounts, entitlements, approval policy, beneficiaries, and transfers.
- Personal accounts, transactions, budgets, card activity, statements, and ledger snapshots.
- Business card activity and a sample dispute.

All seeded users use `password123`.

## Testing Strategy

Backend tests live in `servers/app/tests`:

- `test_auth.py`: authentication behavior.
- `test_business_banking.py`: organization, entitlement, transfer, approval, and related banking workflows.
- `test_calculations.py`: finance calculation modules.

Run:

```bash
cd servers
JWT_SECRET_KEY=dev-secret DATABASE_URL=sqlite:///./finance.db pytest app/tests
```

For manual API verification, use Swagger at `/docs` or the flows in `docs/postman-testing.md`.
