from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class CloudInvoiceSyncError(Base):
    """批次同步中缺必要欄位而未能建立 CloudInvoice 紀錄的失敗筆數追蹤，供健康狀態查詢統計用。

    不重用 cloud_invoice 表：那張表的 invoice_date/amount/seller_name 是 NOT NULL，
    資料本身不完整的錯誤筆數放不進去。這是實作層級的追加（Phase 05 發現的需求），
    不影響任何 Feature 已確認的行為。
    """

    __tablename__ = "cloud_invoice_sync_error"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_number: Mapped[str | None] = mapped_column(String, nullable=True)
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
