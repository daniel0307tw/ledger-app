from pydantic import BaseModel, Field


class CategorySummaryOut(BaseModel):
    category: str
    total_amount: float = Field(serialization_alias="totalAmount")
