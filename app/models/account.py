import enum

from sqlalchemy import String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class AccountType(str, enum.Enum):
    GENERAL = "一般帳戶"
    CREDIT_CARD = "信用卡"


class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[AccountType] = mapped_column(
        SAEnum(AccountType, name="account_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
