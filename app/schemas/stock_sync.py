from typing import Literal

from pydantic import BaseModel, Field


class StockSyncTransactionInput(BaseModel):
    direction: Literal["收入", "支出"]
    amount: float = Field(gt=0)
    currency: Literal["TWD", "USD"]
    account_name: str = Field(alias="accountName")

    model_config = {"populate_by_name": True}


class StockSyncTransactionUpdateInput(BaseModel):
    amount: float = Field(gt=0)
    direction: Literal["收入", "支出"]

    model_config = {"populate_by_name": True}


class StockSyncTransactionOut(BaseModel):
    id: int
    amount: float
    currency: str
    type: str
    is_stock_sync: bool = Field(serialization_alias="isStockSync")
    is_transfer: bool = Field(serialization_alias="isTransfer")
    category_id: int | None = Field(serialization_alias="categoryId")

    model_config = {"from_attributes": True}
