import enum

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class BudgetScope(str, enum.Enum):
    TOTAL = "總預算"
    CATEGORY = "分類預算"


class Budget(Base):
    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scope: Mapped[BudgetScope] = mapped_column(
        SAEnum(BudgetScope, name="budget_scope", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
    monthly_amount: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
