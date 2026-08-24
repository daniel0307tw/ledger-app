from datetime import date

from pydantic import BaseModel, Field


class TransferInput(BaseModel):
    from_account_id: int = Field(alias="fromAccountId")
    to_account_id: int = Field(alias="toAccountId")
    amount: float = Field(gt=0)
    date: date

    model_config = {"populate_by_name": True}
