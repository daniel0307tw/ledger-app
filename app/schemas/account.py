from typing import Literal

from pydantic import BaseModel, Field


class AccountInput(BaseModel):
    name: str = Field(min_length=1)
    type: Literal["一般帳戶", "信用卡"]


class AccountOut(BaseModel):
    id: int
    name: str
    type: str
    balance: float

    model_config = {"from_attributes": True}
