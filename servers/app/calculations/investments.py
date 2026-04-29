from decimal import Decimal


def compound_growth(principal: Decimal, annual_rate: Decimal, years: int, monthly_contribution: Decimal = Decimal("0")) -> float:
    monthly_rate = annual_rate / Decimal("100") / Decimal("12")
    value = principal
    for _ in range(years * 12):
        value = (value + monthly_contribution) * (1 + monthly_rate)
    return round(float(value), 2)
