from decimal import Decimal
import numpy as np
import pandas as pd


def cash_flow_summary(transactions: list[dict]) -> dict:
    frame = pd.DataFrame(transactions)
    if frame.empty:
        return {"total_income": 0, "total_expenses": 0, "net_cash_flow": 0, "savings_rate": 0, "monthly_burn_rate": 0}
    income = Decimal(str(frame.loc[frame["type"].eq("income"), "amount"].sum()))
    expenses = Decimal(str(frame.loc[frame["type"].eq("expense"), "amount"].sum()))
    net = income - expenses
    months = max(1, frame["month"].nunique())
    return {
        "total_income": round(float(income), 2),
        "total_expenses": round(float(expenses), 2),
        "net_cash_flow": round(float(net), 2),
        "savings_rate": round(float((net / income) * 100), 2) if income else 0,
        "monthly_burn_rate": round(float(expenses) / months, 2),
    }


def forecast_cash_flow(monthly_net_flows: list[float], periods: int = 3) -> list[float]:
    if not monthly_net_flows:
        return [0 for _ in range(periods)]
    weights = np.linspace(1, 2, num=len(monthly_net_flows))
    weighted_average = np.average(monthly_net_flows, weights=weights)
    return [round(float(weighted_average), 2) for _ in range(periods)]
