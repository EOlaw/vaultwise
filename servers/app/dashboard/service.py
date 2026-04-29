from collections import defaultdict
from datetime import date
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..accounts.models import Account
from ..accounts.service import account_balance, accessible_account_ids
from ..budgets.models import Budget
from ..budgets.service import serialize_budget
from ..calculations.budgeting import financial_health_score
from ..calculations.cash_flow import cash_flow_summary, forecast_cash_flow
from ..calculations.debt import debt_to_income_ratio
from ..calculations.forecasting import recurring_prediction
from ..calculations.net_worth import calculate_net_worth
from ..transactions.models import Transaction, TransactionType


def transaction_dicts(transactions: list[Transaction]) -> list[dict]:
    return [
        {
            "id": t.id,
            "type": t.type.value,
            "amount": float(t.amount),
            "category": t.category,
            "month": t.occurred_on.strftime("%Y-%m"),
            "occurred_on": t.occurred_on.isoformat(),
            "recurring_rule": t.recurring_rule,
        }
        for t in transactions
    ]


def dashboard_data(db: Session, user_id: int) -> dict:
    account_ids = accessible_account_ids(db, user_id)
    transactions = db.scalars(
        select(Transaction)
        .where(Transaction.account_id.in_(account_ids) if account_ids else Transaction.id == -1)
        .order_by(Transaction.occurred_on)
    ).all()
    accounts = db.scalars(
        select(Account)
        .where(Account.id.in_(account_ids) if account_ids else Account.id == -1)
        .order_by(Account.name)
    ).all()
    budgets = db.scalars(select(Budget).where(Budget.user_id == user_id)).all()
    tx = transaction_dicts(transactions)
    summary = cash_flow_summary(tx)

    accounts_payload = [
        {"id": account.id, "name": account.name, "type": account.type.value, "current_balance": float(account_balance(db, account))}
        for account in accounts
    ]
    category_spend = defaultdict(float)
    monthly = defaultdict(lambda: {"month": "", "income": 0, "expenses": 0, "net": 0})
    debt_payments = Decimal("0")
    for t in transactions:
        month = t.occurred_on.strftime("%Y-%m")
        monthly[month]["month"] = month
        if t.type == TransactionType.income:
            monthly[month]["income"] += float(t.amount)
        elif t.type == TransactionType.expense:
            monthly[month]["expenses"] += float(t.amount)
            category_spend[t.category] += float(t.amount)
            if "debt" in t.category.lower() or "loan" in t.category.lower():
                debt_payments += Decimal(t.amount)
        monthly[month]["net"] = monthly[month]["income"] - monthly[month]["expenses"]

    total_expenses = summary["total_expenses"]
    category_percentages = [
        {"category": category, "amount": round(amount, 2), "percentage": round(amount / total_expenses * 100, 2) if total_expenses else 0}
        for category, amount in sorted(category_spend.items(), key=lambda item: item[1], reverse=True)
    ]
    budget_payload = [serialize_budget(db, budget) for budget in budgets]
    total_budget = sum(float(b["limit_amount"]) for b in budget_payload)
    total_budget_spent = sum(float(b["spent"]) for b in budget_payload)
    monthly_income = Decimal(str(summary["total_income"] / max(1, len(monthly))))
    dti = debt_to_income_ratio(debt_payments / Decimal(max(1, len(monthly))), monthly_income)
    cash_accounts = sum(a["current_balance"] for a in accounts_payload if a["type"] in {"cash", "bank"})
    emergency_months = round(cash_accounts / summary["monthly_burn_rate"], 2) if summary["monthly_burn_rate"] else 0
    budget_progress = total_budget_spent / total_budget * 100 if total_budget else 0
    monthly_rows = list(monthly.values())

    return {
        "summary": {
            **summary,
            "net_worth": calculate_net_worth(accounts_payload),
            "debt_to_income_ratio": dti,
            "emergency_fund_coverage_months": emergency_months,
            "financial_health_score": financial_health_score(summary["savings_rate"], dti, emergency_months, budget_progress),
            "tax_estimate_placeholder": round(summary["total_income"] * 0.22, 2),
        },
        "accounts": accounts_payload,
        "income_vs_expense": [{"name": "Income", "value": summary["total_income"]}, {"name": "Expenses", "value": summary["total_expenses"]}],
        "monthly_cash_flow": monthly_rows,
        "net_worth_trend": [{"month": row["month"], "value": round(sum(r["net"] for r in monthly_rows[:index + 1]), 2)} for index, row in enumerate(monthly_rows)],
        "spending_by_category": category_percentages,
        "budget_progress": budget_payload,
        "top_expenses": [
            {"id": t.id, "category": t.category, "amount": float(t.amount), "occurred_on": t.occurred_on}
            for t in sorted([t for t in transactions if t.type == TransactionType.expense], key=lambda item: item.amount, reverse=True)[:5]
        ],
        "debt_overview": [a for a in accounts_payload if a["type"] in {"credit_card", "loan"}],
        "recent_transactions": transactions[-10:][::-1],
        "cash_flow_forecast": forecast_cash_flow([row["net"] for row in monthly_rows]),
        "recurring_prediction": recurring_prediction(tx),
        "generated_on": date.today(),
    }
