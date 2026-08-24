from typing import Literal

from pydantic import BaseModel, Field


class BudgetInput(BaseModel):
    scope: Literal["總預算", "分類預算"]
    category_id: int | None = Field(default=None, alias="categoryId")
    monthly_amount: float = Field(gt=0, alias="monthlyAmount")

    model_config = {"populate_by_name": True}


class BudgetUpdateInput(BaseModel):
    monthly_amount: float = Field(gt=0, alias="monthlyAmount")

    model_config = {"populate_by_name": True}


class BudgetOut(BaseModel):
    id: int
    scope: str
    category_id: int | None = Field(serialization_alias="categoryId")
    monthly_amount: float = Field(serialization_alias="monthlyAmount")

    model_config = {"from_attributes": True}


class BudgetStatusOut(BaseModel):
    id: int
    scope: str
    category_id: int | None = Field(serialization_alias="categoryId")
    monthly_amount: float = Field(serialization_alias="monthlyAmount")
    spent: float
    remaining: float
    is_over_budget: bool = Field(serialization_alias="isOverBudget")
