# API Notes

FastAPI exposes interactive Swagger documentation at `/docs`.

Banking operations now include business money movement and card servicing:

- `/auth/mfa`, `/auth/step-up`, and `/auth/sessions` provide TOTP enrollment, MFA-required login, recent step-up authorization, trusted-device tracking, refresh-token rotation, and session revocation.
- `/organizations`, `/beneficiaries`, `/transfers`, and `/approvals` model business banking access, payees, dual-control approvals, and transfer posting.
- `/ledger`, `/statements`, and `/notifications` expose available balances, holds, immutable posting entries, account statements, and user alerts.
- `/cards` supports issued debit/credit/virtual cards, spending controls, card authorization decisions, settlement capture, reversal, and authorization holds.
- `/disputes` supports transaction/card disputes, service-case status events, staff-managed review, and provisional credits.

Sensitive POST/PATCH operations for payees, transfers, approvals, cards, and managed disputes require a fresh `/auth/step-up` window. Money movement and settlement endpoints accept `Idempotency-Key` headers so clients can retry safely without duplicate posting.

Financial dashboard fields include:

- total income
- total expenses
- net cash flow
- savings rate
- debt-to-income ratio
- emergency fund coverage
- net worth
- monthly burn rate
- expense category percentages
- cash flow forecast
- recurring transaction prediction
- tax estimate placeholder

CSV export is implemented at `/reports/export.csv`. PDF export is intentionally a production integration point for ReportLab or WeasyPrint.
