from decimal import Decimal
from app.calculations.cash_flow import cash_flow_summary
from app.calculations.debt import loan_payoff
from app.calculations.investments import compound_growth


def test_cash_flow_summary():
    result = cash_flow_summary([
        {"type": "income", "amount": 1000, "month": "2026-04"},
        {"type": "expense", "amount": 250, "month": "2026-04"},
    ])
    assert result["net_cash_flow"] == 750
    assert result["savings_rate"] == 75


def test_loan_payoff():
    result = loan_payoff(Decimal("1000"), Decimal("12"), Decimal("100"))
    assert result["months"] > 10
    assert result["total_interest"] > 0


def test_investment_growth():
    assert compound_growth(Decimal("1000"), Decimal("6"), 1) > 1000
