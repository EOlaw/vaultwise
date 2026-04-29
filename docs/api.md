# API Guide

The FastAPI backend exposes interactive documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Use this file as a technical map of the API surface. Use Swagger or OpenAPI JSON for exact field-level schemas.

## Conventions

- Base URL: `http://localhost:8000`
- JSON content type: `Content-Type: application/json`
- Authentication: `Authorization: Bearer <access_token>`
- Dates: ISO strings such as `2026-04-29`
- Months: `YYYY-MM`, for example `2026-04`
- Money values: decimal-compatible JSON numbers or strings, for example `125.50`
- Most list endpoints return data scoped to the authenticated user's permissions.
- Many business operations can return `403` when the user lacks IAM permission, organization membership, account entitlement, or recent step-up authentication.

## Authentication

### `POST /auth/login`

Request:

```json
{
  "email": "owner@acme.com",
  "password": "password123"
}
```

Response includes:

- `access_token`
- `refresh_token`
- `session_key`
- `token_type`
- `user`

Use `access_token` as the bearer token for protected endpoints.

### `POST /auth/refresh`

Request:

```json
{
  "refresh_token": "{{refresh_token}}"
}
```

Refresh tokens are rotated, so update stored Postman variables after each refresh.

### `POST /auth/step-up`

Step-up creates a short recent-auth window for sensitive operations.

Request:

```json
{
  "password": "password123"
}
```

Sensitive operations will return `403` with `Recent step-up authentication required` when the step-up window is missing or expired.

### MFA And Sessions

- `GET /auth/mfa`: list MFA status and devices.
- `POST /auth/mfa/setup`: create a pending TOTP device.
- `POST /auth/mfa/{device_id}/confirm`: confirm a TOTP code.
- `DELETE /auth/mfa/{device_id}`: remove a device; requires step-up.
- `GET /auth/sessions`: list active sessions.
- `POST /auth/sessions/current/trust`: trust the current device; requires step-up.
- `DELETE /auth/sessions/{session_key}`: revoke a session.
- `POST /auth/logout`: revoke current session.
- `POST /auth/logout-all`: revoke all sessions for current user.

## Idempotency

Retryable money movement and settlement endpoints accept:

```text
Idempotency-Key: {{$guid}}
```

Use this for implemented retry-safe requests that could otherwise create duplicate side effects:

- transfer creation, submission, approval, and cancellation
- approval decisions
- card authorization, capture, and reversal
- dispute status changes

Some other sensitive endpoints still require step-up authentication but do not currently store idempotency records.

## Endpoint Map

### System

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |

### Users And IAM

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/users/me` | Current user |
| `GET` | `/users` | List users |
| `PATCH` | `/users/{user_id}` | Update user |
| `GET` | `/iam/roles` | List roles |
| `GET` | `/iam/permissions` | List permissions |
| `POST` | `/iam/assign-role` | Assign role |
| `GET` | `/iam/policy-decisions` | List authorization decisions |

### Accounts, Transactions, Budgets

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/accounts` | List visible accounts |
| `POST` | `/accounts` | Create account |
| `PATCH` | `/accounts/{account_id}` | Update account |
| `DELETE` | `/accounts/{account_id}` | Delete account |
| `GET` | `/transactions` | List transactions |
| `POST` | `/transactions` | Create transaction |
| `PATCH` | `/transactions/{transaction_id}` | Update transaction |
| `DELETE` | `/transactions/{transaction_id}` | Delete transaction |
| `GET` | `/budgets` | List budgets |
| `POST` | `/budgets` | Create budget |
| `PATCH` | `/budgets/{budget_id}` | Update budget |
| `DELETE` | `/budgets/{budget_id}` | Delete budget |

Example account create:

```json
{
  "name": "Operations Reserve",
  "type": "bank",
  "institution": "BankOS Commercial",
  "opening_balance": "2500.00",
  "interest_rate": "0",
  "organization_id": 1
}
```

Example transaction create:

```json
{
  "account_id": 1,
  "type": "expense",
  "amount": "125.50",
  "occurred_on": "2026-04-29",
  "category": "Software",
  "tags": "saas,tools",
  "notes": "Monthly tool subscription"
}
```

Example budget create:

```json
{
  "month": "2026-04",
  "category": "Software",
  "limit_amount": "800.00"
}
```

### Business Organizations

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/organizations` | List organizations |
| `POST` | `/organizations` | Create organization |
| `GET` | `/organizations/{organization_id}` | Read organization |
| `PATCH` | `/organizations/{organization_id}` | Update organization |
| `GET` | `/organizations/{organization_id}/memberships` | List memberships |
| `POST` | `/organizations/{organization_id}/memberships` | Add membership |
| `PATCH` | `/organizations/{organization_id}/memberships/{membership_id}` | Update membership |
| `GET` | `/organizations/{organization_id}/entitlements` | List entitlements |
| `POST` | `/organizations/{organization_id}/entitlements` | Add entitlement |
| `PATCH` | `/organizations/{organization_id}/entitlements/{entitlement_id}` | Update entitlement |

Example organization create:

```json
{
  "name": "Acme Design Studio",
  "legal_name": "Acme Design Studio LLC",
  "organization_type": "business",
  "tax_id_last4": "4821",
  "industry": "Creative services",
  "country": "United States"
}
```

### Beneficiaries And Transfers

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/beneficiaries` | List payees/beneficiaries |
| `POST` | `/beneficiaries` | Create payee/beneficiary |
| `PATCH` | `/beneficiaries/{beneficiary_id}` | Update payee/beneficiary |
| `GET` | `/transfers` | List transfers |
| `POST` | `/transfers` | Create draft transfer |
| `GET` | `/transfers/{transfer_id}` | Read transfer |
| `POST` | `/transfers/{transfer_id}/submit` | Submit transfer |
| `POST` | `/transfers/{transfer_id}/approve` | Approve transfer |
| `POST` | `/transfers/{transfer_id}/cancel` | Cancel transfer |

Example external beneficiary:

```json
{
  "organization_id": 1,
  "beneficiary_type": "external_ach",
  "display_name": "Vendor ACH",
  "bank_name": "Example Bank",
  "routing_number_last4": "0110",
  "account_number_last4": "9021"
}
```

Example internal transfer:

```json
{
  "organization_id": 1,
  "from_account_id": 1,
  "to_account_id": 2,
  "transfer_type": "internal",
  "amount": "250.00",
  "currency": "USD",
  "memo": "Reserve sweep"
}
```

Example external transfer:

```json
{
  "organization_id": 1,
  "from_account_id": 1,
  "beneficiary_id": 1,
  "transfer_type": "external_ach",
  "amount": "1200.00",
  "currency": "USD",
  "memo": "Vendor payment"
}
```

### Approvals, Risk, Compliance

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/approvals/policies` | List approval policies |
| `POST` | `/approvals/policies` | Create approval policy |
| `PATCH` | `/approvals/policies/{policy_id}` | Update approval policy |
| `GET` | `/approvals` | List approval requests |
| `GET` | `/approvals/{approval_id}` | Read approval request |
| `POST` | `/approvals/{approval_id}/approve` | Approve request |
| `POST` | `/approvals/{approval_id}/reject` | Reject request |
| `GET` | `/risk/alerts` | List risk alerts |
| `GET` | `/risk/alerts/{alert_id}` | Read risk alert |
| `POST` | `/risk/alerts/{alert_id}/assign` | Assign alert |
| `POST` | `/risk/alerts/{alert_id}/resolve` | Resolve alert |
| `POST` | `/risk/alerts/{alert_id}/dismiss` | Dismiss alert |
| `GET` | `/compliance/cases` | List compliance cases |
| `PATCH` | `/compliance/cases/{case_id}` | Update compliance case |

Example approval policy:

```json
{
  "organization_id": 1,
  "name": "Dual control over 1000",
  "transfer_type": null,
  "min_amount": "1000.00",
  "required_approvals": 1,
  "require_separate_approver": true
}
```

Example approval decision:

```json
{
  "notes": "Reviewed entitlement and business purpose."
}
```

### Ledger, Statements, Notifications

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/ledger/accounts/{account_id}/balance` | Available/current balance |
| `GET` | `/ledger/accounts/{account_id}/entries` | Ledger entries |
| `GET` | `/ledger/holds` | Holds |
| `GET` | `/ledger/reconciliation` | Reconciliation summary |
| `POST` | `/ledger/accounts/{account_id}/snapshot` | Create balance snapshot |
| `GET` | `/statements` | List statements |
| `POST` | `/statements/generate` | Generate statement |
| `GET` | `/statements/{statement_id}` | Read statement |
| `GET` | `/notifications` | List notifications |
| `POST` | `/notifications/{notification_id}/read` | Mark notification read |
| `POST` | `/notifications/read-all` | Mark all read |

Example statement generation:

```json
{
  "account_id": 1,
  "period_start": "2026-04-01",
  "period_end": "2026-04-30"
}
```

### Cards And Disputes

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/cards` | List cards |
| `POST` | `/cards` | Issue card |
| `GET` | `/cards/{card_id}` | Read card |
| `PATCH` | `/cards/{card_id}/controls` | Update controls |
| `POST` | `/cards/{card_id}/freeze` | Freeze card |
| `POST` | `/cards/{card_id}/turn-off` | Turn card off |
| `POST` | `/cards/{card_id}/unfreeze` | Unfreeze card |
| `POST` | `/cards/{card_id}/turn-on` | Turn card on |
| `POST` | `/cards/{card_id}/close` | Close card |
| `GET` | `/cards/authorizations/list` | List authorizations |
| `POST` | `/cards/authorizations` | Authorize card transaction |
| `POST` | `/cards/authorizations/{authorization_id}/capture` | Capture authorization |
| `POST` | `/cards/authorizations/{authorization_id}/reverse` | Reverse authorization |
| `GET` | `/disputes` | List disputes |
| `POST` | `/disputes` | Open dispute |
| `GET` | `/disputes/{dispute_id}` | Read dispute |
| `PATCH` | `/disputes/{dispute_id}/status` | Update dispute status |

Example card issue:

```json
{
  "account_id": 1,
  "card_type": "debit",
  "network": "visa",
  "display_name": "Operations Debit",
  "daily_limit": "1000.00",
  "monthly_limit": "5000.00"
}
```

Example card authorization:

```json
{
  "card_id": 1,
  "amount": "42.18",
  "currency": "USD",
  "merchant_name": "Loop Coffee Roasters",
  "merchant_category": "Meals",
  "merchant_country": "US",
  "card_not_present": true,
  "channel": "online"
}
```

Example dispute:

```json
{
  "card_authorization_id": 1,
  "reason": "incorrect_amount",
  "amount": "45.37",
  "description": "Vendor receipt shows a lower amount than the captured authorization."
}
```

### Dashboard, Reports, Analytics

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/dashboard` | Banking dashboard |
| `GET` | `/reports/monthly/{month}` | Monthly summary |
| `GET` | `/reports/yearly/{year}` | Yearly summary |
| `GET` | `/reports/category/{category}` | Category report |
| `GET` | `/reports/export.csv` | CSV export |
| `GET` | `/reports/export.pdf` | PDF placeholder |
| `GET` | `/analytics/summary` | Financial analytics summary |
| `POST` | `/analytics/loan-payoff` | Loan payoff calculator |
| `POST` | `/analytics/investment-growth` | Investment growth calculator |

### Admin

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/admin/metrics` | Admin metrics |
| `GET` | `/admin/audit-logs` | Audit logs |
| `GET` | `/admin/security-events` | Security events |

## Common Status Codes

- `200`: successful read or state transition.
- `201`: resource created.
- `204`: successful delete/logout/no-content operation.
- `400`: invalid business operation or malformed state transition.
- `401`: missing, invalid, expired, or inactive token/session.
- `403`: permission, entitlement, organization, or step-up failure.
- `404`: resource not found or not visible to current user.
- `409`: duplicate/idempotency conflict or state conflict.
- `422`: request body validation failed.
