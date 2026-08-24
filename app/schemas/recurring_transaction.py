from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.transaction import TransactionOut


class RecurringTransactionInput(BaseModel):
    frequency: Literal["每天", "每週", "每月", "每季", "每年", "每三年"]
    amount: float = Field(gt=0)
    category_id: int = Field(alias="categoryId")
    account_id: int = Field(alias="accountId")
    type: Literal["收入", "支出"]
    note: str | None = None
    start_date: date = Field(alias="startDate")
    generate_count: int = Field(gt=0, alias="generateCount")

    model_config = {"populate_by_name": True}


class RecurringTransactionOut(BaseModel):
    id: int
    frequency: str
    amount: float
    category_id: int = Field(serialization_alias="categoryId")
    account_id: int = Field(serialization_alias="accountId")
    type: str
    note: str | None
    start_date: date = Field(serialization_alias="startDate")
    generate_count: int = Field(serialization_alias="generateCount")
    status: str

    model_config = {"from_attributes": True}


class GenerateRecurringTransactionOut(BaseModel):
    generated_count: int = Field(serialization_alias="generatedCount")
    transactions: list[TransactionOut]
