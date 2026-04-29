# Architecture

The Python backend in `servers/` uses a service-layer structure so routes stay thin and business logic remains testable. The Next.js web app lives in `src/`.

- Models define database persistence with SQLAlchemy.
- Schemas validate request and response payloads with Pydantic.
- Services enforce ownership, compute balances, and coordinate writes.
- Banking services enforce organization membership, account entitlements, role permissions, card controls, ledger holds, approvals, dispute staff workflows, recent step-up authorization, and idempotency for retryable money movement.
- Calculation modules isolate finance formulas and Pandas/NumPy analytics.
- Dashboard and report endpoints calculate data from account, transaction, and budget tables.

Production is designed for PostgreSQL with Alembic migrations. Development can run on SQLite using the default `DATABASE_URL`, which helps with fast local testing.

JWT access and refresh tokens protect all finance endpoints. MFA secrets are encrypted at rest, refresh tokens are rotated, sessions track device fingerprints, and RBAC permissions separate customer, business, support, risk, compliance, and bank-admin operations.
