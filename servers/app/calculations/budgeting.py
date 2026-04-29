def financial_health_score(savings_rate: float, debt_to_income: float, emergency_months: float, budget_progress: float) -> int:
    score = 50
    score += min(20, max(-20, savings_rate / 2))
    score += min(20, emergency_months * 4)
    score -= min(25, debt_to_income / 2)
    if budget_progress <= 100:
        score += 10
    else:
        score -= min(20, budget_progress - 100)
    return int(max(0, min(100, round(score))))
