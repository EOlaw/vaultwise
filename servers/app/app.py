from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .accounts import routes as accounts_routes
from .admin import routes as admin_routes
from .analytics import routes as analytics_routes
from .approvals import models as approval_models
from .approvals import routes as approval_routes
from .auth import routes as auth_routes
from .auth import models as auth_models
from .audit import models as audit_models
from .budgets import routes as budgets_routes
from .cards import models as card_models
from .cards import routes as card_routes
from .config import get_settings
from .dashboard import routes as dashboard_routes
from .database import Base, engine
from .disputes import models as dispute_models
from .disputes import routes as dispute_routes
from .iam import models as iam_models
from .iam import routes as iam_routes
from .iam.service import bootstrap_iam
from .ledger import models as ledger_models
from .ledger import routes as ledger_routes
from .notifications import models as notification_models
from .notifications import routes as notification_routes
from .organizations import models as organization_models
from .organizations import routes as organization_routes
from .reports import routes as reports_routes
from .risk import models as risk_models
from .risk import routes as risk_routes
from .statements import models as statement_models
from .statements import routes as statement_routes
from .transfers import models as transfer_models
from .transfers import routes as transfer_routes
from .transactions import routes as transactions_routes
from .users import routes as users_routes
from .utils.dev_migrations import ensure_sqlite_development_schema


settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    if settings.environment == "development":
        ensure_sqlite_development_schema(engine)
        Base.metadata.create_all(bind=engine)
        from .database import SessionLocal
        db = SessionLocal()
        try:
            bootstrap_iam(db)
        finally:
            db.close()


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


app.include_router(auth_routes.router)
app.include_router(users_routes.router)
app.include_router(accounts_routes.router)
app.include_router(transactions_routes.router)
app.include_router(budgets_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(reports_routes.router)
app.include_router(analytics_routes.router)
app.include_router(admin_routes.router)
app.include_router(iam_routes.router)
app.include_router(organization_routes.router)
app.include_router(transfer_routes.beneficiaries_router)
app.include_router(transfer_routes.transfers_router)
app.include_router(approval_routes.router)
app.include_router(risk_routes.risk_router)
app.include_router(risk_routes.compliance_router)
app.include_router(ledger_routes.router)
app.include_router(statement_routes.router)
app.include_router(notification_routes.router)
app.include_router(card_routes.router)
app.include_router(dispute_routes.router)
