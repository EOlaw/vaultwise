from decimal import Decimal


ASSET_TYPES = {"cash", "bank", "investment"}
LIABILITY_TYPES = {"credit_card", "loan"}


def calculate_net_worth(accounts: list[dict]) -> float:
    assets = sum(Decimal(str(account["current_balance"])) for account in accounts if account["type"] in ASSET_TYPES)
    liabilities = sum(Decimal(str(account["current_balance"])) for account in accounts if account["type"] in LIABILITY_TYPES)
    return round(float(assets - liabilities), 2)
