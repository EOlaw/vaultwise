# BankOS Banking Platform

BankOS is a full-stack digital banking and financial operations platform. It combines a FastAPI backend, SQLAlchemy persistence, JWT session security, MFA and step-up authentication, role-based access control, business banking workflows, ledger accounting, card servicing, disputes, reporting, analytics, and a Next.js frontend.

The system is intended to demonstrate how a modern banking application can separate customer-facing workflows from operational, compliance, risk, and administrative controls while keeping core business rules in testable service modules.

## What The System Does

- Personal banking: accounts, transactions, budgets, dashboard metrics, reports, statements, cards, disputes, notifications, and analytics.
- Business banking: organizations, memberships, account entitlements, beneficiaries/payees, transfers, dual-control approvals, risk alerts, compliance cases, ledger holds, and statements.
- Security: access and refresh tokens, refresh-token rotation, session tracking, trusted devices, optional TOTP MFA, step-up windows for sensitive operations, encrypted MFA secrets, and permission-based authorization.
- Money movement: draft transfers, submission, risk screening, approval requirements, authorization holds, posting, cancellation, and idempotent retry protection.
- Card operations: card issuance, controls, freezes, closures, authorization decisions, captures, reversals, and dispute workflows.
- Operations: audit/security events, admin metrics, IAM roles, policy decisions, reconciliation, reporting, and background task placeholders.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic, python-jose, Passlib, Pandas, NumPy, Celery, Redis
- Database: PostgreSQL in Docker, SQLite fallback for local development
- Frontend: Next.js, React, Tailwind CSS, Axios, Recharts, lucide-react
- Testing: Pytest, FastAPI/TestClient, HTTPX

## Project Layout

- `servers/`: FastAPI backend application, database models, routes, services, migrations, seed data, and backend tests.
- `src/`: Next.js frontend application.
- `docs/`: technical architecture, API surface, and Postman testing guidance.
- `docker-compose.yml`: local PostgreSQL, Redis, backend, and frontend composition.

## Quick Start With Docker

```bash
cp servers/.env.example servers/.env
docker compose up --build
```

Open:

- Web app: `http://localhost:3000`
- API health check: `http://localhost:8000/health`
- Swagger docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Local Backend

For SQLite-based local development:

```bash
cd servers
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
JWT_SECRET_KEY=dev-secret DATABASE_URL=sqlite:///./finance.db python -m uvicorn app.app:app --host 127.0.0.1 --port 8000
```

Seed demo users, accounts, business organizations, entitlements, payees, transfers, cards, card activity, disputes, ledger snapshots, and statements:

```bash
cd servers
JWT_SECRET_KEY=dev-secret DATABASE_URL=sqlite:///./finance.db python -m app.utils.seed
```

## Local Frontend

```bash
cd src
npm install
npm run dev
```

The frontend expects the API at `http://localhost:8000` through the shared Axios client.

## Demo Credentials

All seeded users use `password123`.

| Email | Purpose |
| --- | --- |
| `admin@example.com` | Super admin with all permissions |
| `bank.admin@bankos.com` | Bank operations admin |
| `owner@acme.com` | Business owner with Acme organization, accounts, transfers, cards, and approval policy |
| `accountant@acme.com` | Business accountant with read-oriented entitlements |
| `approver@acme.com` | Business approver for dual-control transfer testing |
| `risk@bankos.com` | Risk manager |
| `compliance@bankos.com` | Compliance officer |
| `support@bankos.com` | Support agent for dispute operations |
| `customer@bankos.com` | Personal banking customer |
| `readonly@bankos.com` | Read-only persona for RBAC denial testing |

## Core API Areas

- `/auth`: registration, login, refresh, logout, MFA, step-up auth, sessions, trusted devices.
- `/users`: current user and privileged user management.
- `/accounts`, `/transactions`, `/budgets`: personal and assigned financial data.
- `/organizations`: business profiles, memberships, and account entitlements.
- `/beneficiaries`, `/transfers`, `/approvals`: payees, money movement, and dual-control approvals.
- `/risk`, `/compliance`: transfer screening alerts and compliance case management.
- `/ledger`, `/statements`, `/notifications`: balances, holds, postings, account statements, and user alerts.
- `/cards`, `/disputes`: issued cards, controls, authorizations, captures, reversals, and disputes.
- `/dashboard`, `/reports`, `/analytics`: calculated summaries, exports, and financial calculators.
- `/iam`, `/admin`: roles, permissions, policy decisions, metrics, audit logs, and security events.

## Testing

Backend test suite:

```bash
cd servers
JWT_SECRET_KEY=dev-secret DATABASE_URL=sqlite:///./finance.db pytest app/tests
```

Postman testing is documented in [docs/postman-testing.md](docs/postman-testing.md). The shortest flow is:

1. Start the backend.
2. Seed demo data.
3. Log in with `owner@acme.com` or `customer@bankos.com`.
4. Store `access_token` and `refresh_token` as Postman variables.
5. Send authenticated requests with `Authorization: Bearer {{access_token}}`.
6. For sensitive POST/PATCH operations, call `/auth/step-up` first.
7. For retryable transfer, approval-decision, card authorization/settlement, and dispute-status requests, send an `Idempotency-Key` header.

## Technical Documentation

- [docs/architecture.md](docs/architecture.md): system design, module boundaries, security model, data flow, and operational concerns.
- [docs/api.md](docs/api.md): API conventions, endpoint map, authentication, permissions, idempotency, and common workflows.
- [docs/postman-testing.md](docs/postman-testing.md): Postman environment setup, variables, request examples, and smoke-test flows.

## Environment Variables

The backend reads settings from `servers/.env`.

| Variable | Purpose |
| --- | --- |
| `ENVIRONMENT` | `development` enables SQLite schema creation helpers and IAM bootstrap |
| `DATABASE_URL` | SQLAlchemy connection string |
| `JWT_SECRET_KEY` | Required signing secret for access and refresh tokens |
| `JWT_ALGORITHM` | JWT signing algorithm, default `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime |
| `STEP_UP_EXPIRE_MINUTES` | Recent-auth window for sensitive actions |
| `IDEMPOTENCY_KEY_EXPIRE_HOURS` | Lifetime for idempotent request records |
| `FIELD_ENCRYPTION_KEY` | Optional field encryption key for sensitive secrets |
| `REDIS_URL` | Celery broker/backend URL |
| `CORS_ORIGINS` | Allowed frontend origins |

## Notes For Reviewers

- The backend entrypoint is `app.app:app`; `servers/server.py` runs it with Uvicorn.
- In development, the app can create/update SQLite tables on startup. Production should use Alembic migrations.
- Swagger at `/docs` is the source of truth for exact request/response schemas.
- CSV export is implemented at `/reports/export.csv`; PDF export returns a simple generated banking report at `/reports/export.pdf`.
