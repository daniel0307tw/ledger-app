import enum

from sqlalchemy import String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class CategoryType(str, enum.Enum):
    INCOME = "收入"
    EXPENSE = "支出"
    BOTH = "皆可"


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[CategoryType] = mapped_column(
        SAEnum(CategoryType, name="category_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
