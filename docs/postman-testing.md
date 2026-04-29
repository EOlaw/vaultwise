# Postman Testing Guide

This guide shows how to test BankOS manually with Postman after starting the FastAPI backend and seeding demo data.

## 1. Start The API

SQLite local mode:

```bash
cd servers
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
JWT_SECRET_KEY=dev-secret DATABASE_URL=sqlite:///./finance.db python -m uvicorn app.app:app --host 127.0.0.1 --port 8000
```

Seed demo data in another terminal:

```bash
cd servers
JWT_SECRET_KEY=dev-secret DATABASE_URL=sqlite:///./finance.db python -m app.utils.seed
```

Verify:

```http
GET http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## 2. Create A Postman Environment

Create an environment named `BankOS Local` with these variables:

| Variable | Initial value |
| --- | --- |
| `base_url` | `http://localhost:8000` |
| `access_token` | empty |
| `refresh_token` | empty |
| `session_key` | empty |
| `organization_id` | `1` |
| `account_id` | `1` |
| `to_account_id` | `2` |
| `beneficiary_id` | empty |
| `transfer_id` | empty |
| `approval_id` | empty |
| `card_id` | empty |
| `authorization_id` | empty |
| `dispute_id` | empty |

Set collection-level authorization to `Bearer Token` and use:

```text
{{access_token}}
```

For JSON requests, set:

```text
Content-Type: application/json
```

For retryable transfer, approval-decision, card authorization/settlement, and dispute-status requests, add:

```text
Idempotency-Key: {{$guid}}
```

## 3. Login Request

Create request:

```http
POST {{base_url}}/auth/login
Content-Type: application/json
```

Body:

```json
{
  "email": "owner@acme.com",
  "password": "password123"
}
```

Tests tab:

```javascript
const json = pm.response.json();
pm.environment.set("access_token", json.access_token);
pm.environment.set("refresh_token", json.refresh_token);
pm.environment.set("session_key", json.session_key);
```

Useful seeded logins:

| Email | What to test |
| --- | --- |
| `owner@acme.com` | Business owner workflows |
| `approver@acme.com` | Separate approval decisions |
| `customer@bankos.com` | Personal banking workflows |
| `support@bankos.com` | Dispute management |
| `risk@bankos.com` | Risk alert management |
| `compliance@bankos.com` | Compliance cases |
| `admin@example.com` | Admin and IAM access |
| `readonly@bankos.com` | Permission denial checks |

All seeded users use `password123`.

## 4. Step-Up Request

Run this before sensitive operations such as transfers, approvals, beneficiary changes, card controls, captures, and dispute status updates.

```http
POST {{base_url}}/auth/step-up
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "password": "password123"
}
```

Expected response includes `step_up_expires_at`.

## 5. Basic Smoke Test

### Current User

```http
GET {{base_url}}/users/me
Authorization: Bearer {{access_token}}
```

### Accounts

```http
GET {{base_url}}/accounts
Authorization: Bearer {{access_token}}
```

Tests tab to store the first two accounts:

```javascript
const accounts = pm.response.json();
if (accounts.length > 0) pm.environment.set("account_id", accounts[0].id);
if (accounts.length > 1) pm.environment.set("to_account_id", accounts[1].id);
```

### Dashboard

```http
GET {{base_url}}/dashboard
Authorization: Bearer {{access_token}}
```

### Transactions

```http
GET {{base_url}}/transactions
Authorization: Bearer {{access_token}}
```

### Budgets

```http
GET {{base_url}}/budgets
Authorization: Bearer {{access_token}}
```

## 6. Business Banking Flow

Login as `owner@acme.com`.

### List Organizations

```http
GET {{base_url}}/organizations
Authorization: Bearer {{access_token}}
```

Tests tab:

```javascript
const orgs = pm.response.json();
if (orgs.length > 0) pm.environment.set("organization_id", orgs[0].id);
```

### List Entitlements

```http
GET {{base_url}}/organizations/{{organization_id}}/entitlements
Authorization: Bearer {{access_token}}
```

### Create Beneficiary

Run step-up first.

```http
POST {{base_url}}/beneficiaries
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "organization_id": {{organization_id}},
  "beneficiary_type": "external_ach",
  "display_name": "Postman Vendor ACH",
  "bank_name": "Example Bank",
  "routing_number_last4": "0110",
  "account_number_last4": "9021"
}
```

Tests tab:

```javascript
const json = pm.response.json();
pm.environment.set("beneficiary_id", json.id);
```

### Create Draft Transfer

```http
POST {{base_url}}/transfers
Authorization: Bearer {{access_token}}
Content-Type: application/json
Idempotency-Key: {{$guid}}
```

Body:

```json
{
  "organization_id": {{organization_id}},
  "from_account_id": {{account_id}},
  "beneficiary_id": {{beneficiary_id}},
  "transfer_type": "external_ach",
  "amount": "1200.00",
  "currency": "USD",
  "memo": "Postman vendor payment"
}
```

Tests tab:

```javascript
const json = pm.response.json();
pm.environment.set("transfer_id", json.id);
```

### Submit Transfer

```http
POST {{base_url}}/transfers/{{transfer_id}}/submit
Authorization: Bearer {{access_token}}
Idempotency-Key: {{$guid}}
```

Transfers over the seeded approval threshold can become `pending_approval`.

### Find Approval Request

```http
GET {{base_url}}/approvals
Authorization: Bearer {{access_token}}
```

Tests tab:

```javascript
const approvals = pm.response.json();
const pending = approvals.find((item) => item.transfer_id == pm.environment.get("transfer_id"));
if (pending) pm.environment.set("approval_id", pending.id);
```

### Approve With A Separate Approver

Login again as `approver@acme.com`, run step-up, then:

```http
POST {{base_url}}/approvals/{{approval_id}}/approve
Authorization: Bearer {{access_token}}
Content-Type: application/json
Idempotency-Key: {{$guid}}
```

Body:

```json
{
  "notes": "Approved from Postman after reviewing transfer details."
}
```

## 7. Ledger And Statement Checks

```http
GET {{base_url}}/ledger/accounts/{{account_id}}/balance
Authorization: Bearer {{access_token}}
```

```http
GET {{base_url}}/ledger/accounts/{{account_id}}/entries
Authorization: Bearer {{access_token}}
```

```http
GET {{base_url}}/ledger/holds
Authorization: Bearer {{access_token}}
```

Generate a statement:

```http
POST {{base_url}}/statements/generate
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "account_id": {{account_id}},
  "period_start": "2026-04-01",
  "period_end": "2026-04-30"
}
```

## 8. Card Flow

Login as `customer@bankos.com` or `owner@acme.com`. Run step-up before card mutations.

### List Cards

```http
GET {{base_url}}/cards
Authorization: Bearer {{access_token}}
```

Tests tab:

```javascript
const cards = pm.response.json();
if (cards.length > 0) pm.environment.set("card_id", cards[0].id);
```

### Issue Card

```http
POST {{base_url}}/cards
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "account_id": {{account_id}},
  "card_type": "debit",
  "network": "visa",
  "display_name": "Postman Debit",
  "daily_limit": "1000.00",
  "monthly_limit": "5000.00"
}
```

### Update Controls

```http
PATCH {{base_url}}/cards/{{card_id}}/controls
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "allow_online": true,
  "allow_international": false,
  "allow_atm": true,
  "max_transaction_amount": "250.00",
  "blocked_merchant_categories": "Gambling,Cash Advance"
}
```

### Authorize Card Transaction

```http
POST {{base_url}}/cards/authorizations
Authorization: Bearer {{access_token}}
Content-Type: application/json
Idempotency-Key: {{$guid}}
```

Body:

```json
{
  "card_id": {{card_id}},
  "amount": "42.18",
  "currency": "USD",
  "merchant_name": "Loop Coffee Roasters",
  "merchant_category": "Meals",
  "merchant_country": "US",
  "card_not_present": true,
  "channel": "online"
}
```

Tests tab:

```javascript
const json = pm.response.json();
pm.environment.set("authorization_id", json.id);
```

### Capture Authorization

```http
POST {{base_url}}/cards/authorizations/{{authorization_id}}/capture
Authorization: Bearer {{access_token}}
Idempotency-Key: {{$guid}}
```

## 9. Dispute Flow

Open a dispute as the customer or business owner:

```http
POST {{base_url}}/disputes
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "card_authorization_id": {{authorization_id}},
  "reason": "incorrect_amount",
  "amount": "10.00",
  "description": "The posted amount does not match my receipt."
}
```

Tests tab:

```javascript
const json = pm.response.json();
pm.environment.set("dispute_id", json.id);
```

To test staff management, login as `support@bankos.com`, run step-up, then:

```http
PATCH {{base_url}}/disputes/{{dispute_id}}/status
Authorization: Bearer {{access_token}}
Content-Type: application/json
Idempotency-Key: {{$guid}}
```

Body:

```json
{
  "status": "provisional_credit",
  "notes": "Temporary credit issued while claim is reviewed."
}
```

## 10. Reports And Analytics

```http
GET {{base_url}}/reports/monthly/2026-04
Authorization: Bearer {{access_token}}
```

```http
GET {{base_url}}/reports/export.csv
Authorization: Bearer {{access_token}}
```

```http
GET {{base_url}}/analytics/summary
Authorization: Bearer {{access_token}}
```

Loan payoff calculator:

```http
POST {{base_url}}/analytics/loan-payoff
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Use Swagger at `/docs` to confirm the current calculator request schema.

## 11. RBAC Denial Test

Login as `readonly@bankos.com`, then try to create an account:

```http
POST {{base_url}}/accounts
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

Body:

```json
{
  "name": "Should Fail",
  "type": "bank",
  "institution": "BankOS Retail",
  "opening_balance": "100.00"
}
```

Expected result: `403` permission denial.

## Troubleshooting

- `401 Unauthorized`: login again and refresh the `access_token` variable.
- `403 Recent step-up authentication required`: call `/auth/step-up` with the current user password.
- `403` permission denial: switch to a user with the required role or verify organization entitlements.
- `404`: the resource may belong to another user or organization.
- `422`: compare the request body with Swagger at `/docs`.
- Empty data: run `python -m app.utils.seed` with the same database settings used by the running API.
