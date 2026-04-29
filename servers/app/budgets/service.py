from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models import Budget
from .schemas import BudgetCreate
from ..transactions.models import Transaction, TransactionType


def owned_budget(db: Session, user_id: int, budget_id: int) -> Budget:
    budget = db.scalar(select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id))
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return budget


def create_budget(db: Session, user_id: int, payload: BudgetCreate) -> Budget:
    budget = Budget(user_id=user_id, **payload.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def spent_for_budget(db: Session, budget: Budget) -> Decimal:
    start = f"{budget.month}-01"
    end = f"{budget.month}-31"
    spent = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.user_id == budget.user_id,
        Transaction.type == TransactionType.expense,
        Transaction.category == budget.category,
        Transaction.occurred_on >= start,
        Transaction.occurred_on <= end,
    ))
    return Decimal(spent or 0)


def serialize_budget(db: Session, budget: Budget) -> dict:
    spent = spent_for_budget(db, budget)
    limit = Decimal(budget.limit_amount)
    return {
        **budget.__dict__,
        "spent": spent,
        "remaining": limit - spent,
        "progress": round(float(spent / limit * 100), 2) if limit else 0,
        "overspent": spent > limit,
    }
