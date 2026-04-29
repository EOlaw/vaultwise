from decimal import Decimal
from pydantic import BaseModel, Field, StringConstraints
from typing import Annotated

BudgetMonth = Annotated[str, StringConstraints(pattern=r"^\d{4}-\d{2}$")]


class BudgetCreate(BaseModel):
    month: BudgetMonth
    category: str = Field(min_length=2, max_length=80)
    limit_amount: Decimal = Field(gt=0)


class BudgetUpdate(BaseModel):
    limit_amount: Decimal = Field(gt=0)


class BudgetRead(BudgetCreate):
    id: int
    spent: Decimal = 0
    remaining: Decimal = 0
    progress: float = 0
    overspent: bool = False

    model_config = {"from_attributes": True}
