from collections import defaultdict
from decimal import Decimal


def recurring_prediction(transactions: list[dict]) -> dict:
    totals = defaultdict(Decimal)
    for transaction in transactions:
        if transaction.get("recurring_rule"):
            totals[transaction["type"]] += Decimal(str(transaction["amount"]))
    return {key: round(float(value), 2) for key, value in totals.items()}
