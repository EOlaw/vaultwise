from decimal import Decimal
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..calculations.debt import loan_payoff
from ..calculations.investments import compound_growth
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from ..dashboard.service import dashboard_data


router = APIRouter(prefix="/analytics", tags=["analytics"])


class LoanPayoffRequest(BaseModel):
    balance: Decimal
    annual_rate: Decimal
    monthly_payment: Decimal


class InvestmentProjectionRequest(BaseModel):
    principal: Decimal
    annual_rate: Decimal
    years: int
    monthly_contribution: Decimal = Decimal("0")


@router.get("/summary")
def summary(db: Session = Depends(get_db), user: User = Depends(require_permission("analytics:read"))):
    return dashboard_data(db, user.id)["summary"]


@router.post("/loan-payoff")
def payoff(payload: LoanPayoffRequest, _: User = Depends(require_permission("analytics:calculate"))):
    return loan_payoff(payload.balance, payload.annual_rate, payload.monthly_payment)


@router.post("/investment-growth")
def investment_growth(payload: InvestmentProjectionRequest, _: User = Depends(require_permission("analytics:calculate"))):
    return {"future_value": compound_growth(payload.principal, payload.annual_rate, payload.years, payload.monthly_contribution)}
