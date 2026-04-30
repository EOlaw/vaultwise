# 🚀 Full-Stack Digital Banking Platform with Enterprise-Grade Security & Dual-Control Approvals
> VaultWise — A production-ready banking OS handling personal finance, business banking, risk screening, and compliance workflows end-to-end

---

## 🔍 Problem
- Modern banking applications struggle to unify personal banking, business operations, compliance, and risk management in a single, secure platform
- Financial institutions face critical risks from weak authentication, uncontrolled money movement, and lack of audit trails — leading to fraud, regulatory penalties, and operational failures
- Business banking workflows require multi-party approval controls that off-the-shelf solutions rarely support natively, increasing the risk of unauthorized or erroneous transactions
- Developers and fintech teams have no clean reference architecture demonstrating how a real-world banking backend should separate concerns while remaining testable and extensible

---

## 💡 Solution
- Built a full-stack digital banking platform that:
  - Implements end-to-end personal and business banking workflows — accounts, transfers, cards, disputes, statements, and analytics — within a single unified system
  - Engineered a multi-layered security model featuring JWT access/refresh token rotation, TOTP MFA, step-up authentication windows, trusted device tracking, and field-level encryption for sensitive secrets
  - Designed a dual-control approval engine for business transfers, ensuring no single user can unilaterally move funds without a designated approver
  - Built a risk screening and compliance case management layer that flags, holds, and escalates suspicious transactions before they post to the ledger
  - Delivered a fully interactive Next.js frontend with real-time dashboard metrics, financial charts, and role-aware UI rendering

---

## 🧠 Tech Stack
- **Languages:** Python, TypeScript, SQL
- **Backend:** FastAPI, SQLAlchemy, Alembic, Pydantic, python-jose, Passlib
- **Data:** Pandas, NumPy
- **Database:** PostgreSQL (production), SQLite (local dev fallback)
- **Frontend:** Next.js, React, Tailwind CSS, Recharts, Axios
- **Auth & Security:** JWT (HS256), TOTP MFA, bcrypt, optional field encryption
- **Task Queue:** Celery, Redis
- **Testing:** Pytest, FastAPI TestClient, HTTPX
- **Tools:** Docker, Docker Compose, Uvicorn, Swagger/OpenAPI, Postman

---

## 🏗 Architecture
- **Data ingestion** from frontend client requests and seed scripts simulating real banking events (registrations, transfers, card activity, disputes)
- **Processing** via FastAPI service modules enforcing business rules — risk screening, approval gating, idempotency checks, and ledger posting
- **Storage** in PostgreSQL with Alembic-managed migrations; SQLite for rapid local development
- **Security layer** wraps every sensitive route with JWT validation, permission checks, and step-up auth enforcement before any state mutation occurs
- **Output** served through a REST API consumed by the Next.js frontend, with Swagger docs at `/docs` and CSV/PDF report exports at `/reports`

```
Client (Next.js)
     │
     ▼
FastAPI Router Layer
     │
     ├── Auth & Session Services (JWT, MFA, Step-Up)
     ├── Banking Services (Accounts, Transfers, Cards, Disputes)
     ├── Risk & Compliance Services (Screening, Holds, Cases)
     ├── Ledger & Reporting Services (Postings, Statements, Analytics)
     └── IAM & Admin Services (Roles, Audit Logs, Metrics)
          │
          ▼
    PostgreSQL / SQLite
```

---

## ⚙️ How It Works
1. Users register and authenticate via `/auth`; sessions are tracked with rotating refresh tokens and optional TOTP MFA
2. Authenticated requests pass through role-based access control — permissions are evaluated per endpoint before any data is read or mutated
3. Transfers are drafted, submitted, and screened by the risk engine; flagged transfers trigger compliance cases and are held from posting until reviewed
4. Business transfers above threshold require a second approver via the dual-control approval workflow before funds move
5. Approved transfers post to the ledger, update account balances, and generate statements and notifications
6. Card operations (issuance, freeze, authorization, capture, dispute) flow through a dedicated card servicing module with full reversal support
7. Admins and operations staff access audit logs, security events, reconciliation reports, and dashboard metrics through privileged IAM-gated endpoints

---

## 🧠 Key Techniques
- JWT Access & Refresh Token Rotation with session invalidation
- Step-Up Authentication for sensitive operations (transfers, card changes, admin actions)
- Dual-Control Approval Engine for business-grade transfer authorization
- Risk Screening Pipeline with hold management and compliance escalation
- Ledger Accounting with idempotent posting, reversal, and reconciliation
- Role-Based Access Control (RBAC) with fine-grained permission policies
- Field-Level Encryption for MFA secrets and sensitive credentials
- Idempotency Key enforcement on all retryable financial operations
- RESTful API design with full OpenAPI/Swagger documentation

---

## 📊 Results / Impact
- Supports 10+ distinct user roles (admin, compliance, risk, support, business owner, approver, accountant, customer) within a single unified permission model
- Covers 15+ API domains with over 80 endpoints across auth, banking, compliance, cards, ledger, reporting, and admin
- Dual-control approval workflow reduces unauthorized transfer risk to near zero for business accounts
- Idempotency protection on all financial operations eliminates double-posting under retry conditions
- Full test suite covering authentication flows, banking operations, and permission boundaries

---

## 💡 Business Impact
- Reduces fraud and unauthorized transaction risk through multi-factor authentication, step-up windows, and dual-control approvals
- Accelerates compliance readiness with built-in risk screening, compliance case management, and full audit trail logging
- Improves operational efficiency by consolidating personal banking, business banking, card servicing, and reporting into one deployable platform
- Increases system reliability and developer confidence through idempotency enforcement, token rotation, and a fully documented API surface

---

## 📌 Key Takeaways
- Demonstrates strong skills in full-stack engineering, financial systems design, API development, and security architecture
- Built a scalable, production-ready platform with Docker-based deployment, Alembic-managed schema migrations, and environment-driven configuration
- Applied real-world banking domain knowledge — ledger accounting, dual-control workflows, risk screening, and compliance — with measurable system-level controls
- Identified areas for future improvement: async background job processing via Celery, event-driven ledger reconciliation, and enhanced fraud ML scoring on the risk pipeline
