from decimal import Decimal


def debt_to_income_ratio(monthly_debt_payments: Decimal, monthly_income: Decimal) -> float:
    if monthly_income <= 0:
        return 0
    return round(float(monthly_debt_payments / monthly_income * 100), 2)


def loan_payoff(balance: Decimal, annual_rate: Decimal, monthly_payment: Decimal) -> dict:
    if balance <= 0 or monthly_payment <= 0:
        return {"months": 0, "total_interest": 0}
    monthly_rate = annual_rate / Decimal("100") / Decimal("12")
    months = 0
    interest_paid = Decimal("0")
    remaining = balance
    while remaining > 0 and months < 600:
        interest = remaining * monthly_rate
        principal = monthly_payment - interest
        if principal <= 0:
            return {"months": None, "total_interest": None, "message": "Payment does not cover accruing interest"}
        remaining -= principal
        interest_paid += interest
        months += 1
    return {"months": months, "total_interest": round(float(interest_paid), 2)}
