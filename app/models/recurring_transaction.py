import enum
from datetime import date as date_type

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.ledger_transaction import TransactionType


class RecurringFrequency(str, enum.Enum):
    DAILY = "每天"
    WEEKLY = "每週"
    MONTHLY = "每月"
    QUARTERLY = "每季"
    YEARLY = "每年"
    TRIENNIAL = "每三年"


class RecurringTransactionStatus(str, enum.Enum):
    ENABLED = "啟用"
    DISABLED = "停用"


class RecurringTransaction(Base):
    __tablename__ = "recurring_transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    frequency: Mapped[RecurringFrequency] = mapped_column(
        SAEnum(RecurringFrequency, name="recurring_frequency", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name="transaction_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    generate_count: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[RecurringTransactionStatus] = mapped_column(
        SAEnum(
            RecurringTransactionStatus,
            name="recurring_transaction_status",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
        default=RecurringTransactionStatus.ENABLED,
    )
