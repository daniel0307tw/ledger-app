import enum
from datetime import date as date_type

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class TransactionType(str, enum.Enum):
    INCOME = "收入"
    EXPENSE = "支出"


class SyncStatus(str, enum.Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"


class AdvancePaymentStatus(str, enum.Enum):
    PENDING = "pending"
    SETTLED = "settled"


class LedgerTransaction(Base):
    __tablename__ = "ledger_transaction"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("category.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(String, nullable=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name="transaction_type", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
    )
    is_transfer: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    transfer_group_id: Mapped[str | None] = mapped_column(String, nullable=True)
    sync_status: Mapped[SyncStatus] = mapped_column(
        SAEnum(SyncStatus, name="sync_status_enum", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=SyncStatus.PENDING,
    )
    cash_position_id: Mapped[int | None] = mapped_column(nullable=True)
    source_recurring_transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("recurring_transaction.id", ondelete="SET NULL"), nullable=True
    )
    advance_payment_amount: Mapped[float | None] = mapped_column(Numeric(14, 4), nullable=True)
    advance_payment_status: Mapped[AdvancePaymentStatus | None] = mapped_column(
        SAEnum(
            AdvancePaymentStatus,
            name="advance_payment_status_enum",
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=True,
    )
    # 比照 source_recurring_transaction_id 的單向 FK 模式：ondelete=SET NULL，讓刪除還款交易時
    # 不會被 FK 擋下（service 層雖然已手動先清空再刪除，這裡的 SET NULL 是額外的資料庫層防線）。
    settlement_transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("ledger_transaction.id", ondelete="SET NULL"), nullable=True
    )
