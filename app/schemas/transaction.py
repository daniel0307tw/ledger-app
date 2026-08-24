from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class TransactionInput(BaseModel):
    date: date
    amount: float = Field(gt=0)
    category_id: int = Field(alias="categoryId")
    account_id: int = Field(alias="accountId")
    type: Literal["收入", "支出"]
    note: str | None = None
    advance_payment_amount: float | None = Field(default=None, gt=0, alias="advancePaymentAmount")

    model_config = {"populate_by_name": True}


class TransactionOut(BaseModel):
    id: int
    date: date
    amount: float
    category_id: int | None = Field(serialization_alias="categoryId")
    account_id: int = Field(serialization_alias="accountId")
    type: str
    note: str | None
    is_transfer: bool = Field(serialization_alias="isTransfer")
    transfer_group_id: str | None = Field(serialization_alias="transferGroupId")
    sync_status: str = Field(serialization_alias="syncStatus")
    cash_position_id: int | None = Field(serialization_alias="cashPositionId")
    advance_payment_amount: float | None = Field(serialization_alias="advancePaymentAmount")
    advance_payment_status: str | None = Field(serialization_alias="advancePaymentStatus")
    settlement_transaction_id: int | None = Field(serialization_alias="settlementTransactionId")

    model_config = {"from_attributes": True}


class SettleAdvancePaymentInput(BaseModel):
    date: date
    amount: float = Field(gt=0)
    account_id: int = Field(alias="accountId")

    model_config = {"populate_by_name": True}
