# BankOS Banking Platform

A full-stack digital banking and financial operations platform with a Python FastAPI backend, SQLAlchemy data model, JWT auth, role-based access, analytics calculations, and a Next.js frontend.

## Stack

- Backend: Python, FastAPI, SQLAlchemy, Alembic, Pydantic, JWT, Pandas, NumPy, Celery, Redis
- Database: PostgreSQL in Docker, SQLite fallback for local development
- Frontend: Next.js, React, Tailwind CSS, Axios, Recharts, lucide-react

## Project Layout

- `servers/`: Python FastAPI backend
- `src/`: Next.js web app
- `docs/`: architecture and API notes

## Quick Start

```bash
cp servers/.env.example servers/.env
docker compose up --build
```

Open:

- Web app: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

## Local Backend

```bash
cd servers
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Seed demo banking users, organization data, entitlements, payees, transfers, cards, card activity, and disputes:

```bash
cd servers
python -m app.utils.seed
```

Demo credentials after seeding:

- `admin@example.com` / `password123` - super admin
- `bank.admin@bankos.com` / `password123` - bank operations admin
- `owner@acme.com` / `password123` - business owner
- `accountant@acme.com` / `password123` - entitled business accountant
- `approver@acme.com` / `password123` - business transfer approver
- `risk@bankos.com` / `password123` - risk manager
- `compliance@bankos.com` / `password123` - compliance officer
- `support@bankos.com` / `password123` - support agent for dispute operations
- `customer@bankos.com` / `password123` - personal banking customer
- `readonly@bankos.com` / `password123` - read-only user

## Local Frontend

```bash
cd src
npm install
npm run dev
```

## API Areas

- `/auth`: register, login, refresh
- `/auth/mfa`, `/auth/step-up`, `/auth/sessions`: TOTP MFA, recent step-up auth, trusted devices, session revocation
- `/users`: current user and admin user management
- `/accounts`: cash, bank, credit card, investment, and loan accounts
- `/transactions`: income, expense, transfer records, tags, notes, receipts, recurring rules
- `/budgets`: monthly/category budgets and budget progress
- `/organizations`: business profiles, memberships, and account entitlements
- `/beneficiaries`: internal/external beneficiaries and payees
- `/transfers`: draft, submitted, approved, cancelled, posted transfer workflows
- `/approvals`: approval policies, approval queues, approve/reject decisions
- `/risk`: risk alerts from transfer screening rules
- `/compliance`: compliance cases opened from high-severity risk alerts
- `/ledger`: available balances, holds, ledger entries, and balance snapshots
- `/statements`: generated account statements and statement line items
- `/notifications`: user banking notifications and read tracking
- `/cards`: issued cards, card controls, authorization holds, captures, and reversals
- `/disputes`: transaction/card disputes, lifecycle events, and provisional credits
- `/dashboard`: calculated banking dashboard data from database records
- `/reports`: monthly, yearly, category, CSV/PDF export placeholder
- `/analytics`: financial summary, loan payoff, investment growth
- `/admin`: system metrics, audit logs, and security events

## Tests

```bash
cd servers
pytest app/tests
```
