from typing import Literal

from pydantic import BaseModel, Field


class CategoryInput(BaseModel):
    name: str = Field(min_length=1)
    type: Literal["收入", "支出", "皆可"]


class CategoryOut(BaseModel):
    id: int
    name: str
    type: str

    model_config = {"from_attributes": True}
