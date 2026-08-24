import enum
from datetime import date as date_type
from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class CloudInvoiceStatus(str, enum.Enum):
    PENDING_REVIEW = "pending_review"
    SYNCED = "synced"
    SKIPPED = "skipped"


class CloudInvoice(Base):
    __tablename__ = "cloud_invoice"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_number: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    invoice_date: Mapped[date_type] = mapped_column(Date, nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 4), nullable=False)
    seller_name: Mapped[str] = mapped_column(String, nullable=False)
    item_summary: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[CloudInvoiceStatus] = mapped_column(
        SAEnum(CloudInvoiceStatus, name="cloud_invoice_status", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=CloudInvoiceStatus.PENDING_REVIEW,
    )
    transaction_id: Mapped[int | None] = mapped_column(
        ForeignKey("ledger_transaction.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
