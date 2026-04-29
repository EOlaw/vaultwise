from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..database import get_db
from ..dependencies import require_permission
from ..users.models import User
from .models import Budget
from .schemas import BudgetCreate, BudgetRead, BudgetUpdate
from .service import create_budget, owned_budget, serialize_budget


router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetRead])
def list_budgets(month: str | None = None, db: Session = Depends(get_db), user: User = Depends(require_permission("budgets:read"))):
    query = select(Budget).where(Budget.user_id == user.id)
    if month:
        query = query.where(Budget.month == month)
    budgets = db.scalars(query.order_by(Budget.month.desc(), Budget.category)).all()
    return [serialize_budget(db, budget) for budget in budgets]


@router.post("", response_model=BudgetRead, status_code=201)
def create(payload: BudgetCreate, db: Session = Depends(get_db), user: User = Depends(require_permission("budgets:create"))):
    return serialize_budget(db, create_budget(db, user.id, payload))


@router.patch("/{budget_id}", response_model=BudgetRead)
def patch(budget_id: int, payload: BudgetUpdate, db: Session = Depends(get_db), user: User = Depends(require_permission("budgets:update"))):
    budget = owned_budget(db, user.id, budget_id)
    budget.limit_amount = payload.limit_amount
    db.commit()
    db.refresh(budget)
    return serialize_budget(db, budget)


@router.delete("/{budget_id}", status_code=204)
def delete(budget_id: int, db: Session = Depends(get_db), user: User = Depends(require_permission("budgets:delete"))):
    budget = owned_budget(db, user.id, budget_id)
    db.delete(budget)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
