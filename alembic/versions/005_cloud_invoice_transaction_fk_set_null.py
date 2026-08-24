"""cloud_invoice.transaction_id FK: add ON DELETE SET NULL

Revision ID: 005
Revises: 004
Create Date: 2026-08-24

實測踩到的坑（Phase 07 Integration Validation）：刪除一筆已透過雲端發票同步建立的
ledger_transaction 時，若沒有 ON DELETE 行為，會被 FK 擋下（IntegrityError，前端只會看到
Internal Server Error，沒有清楚錯誤訊息）。使用者刪除交易是既有、完全合法的操作，不應該因為
這筆交易恰好來自雲端發票同步就被卡住——比照 source_recurring_transaction_id 的既有設計
（同樣是「交易本身才是真相，來源連結遺失可以接受」），改成 SET NULL。
"""

import sqlalchemy as sa
from alembic import op

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("cloud_invoice_transaction_id_fkey", "cloud_invoice", type_="foreignkey")
    op.create_foreign_key(
        "cloud_invoice_transaction_id_fkey",
        "cloud_invoice",
        "ledger_transaction",
        ["transaction_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("cloud_invoice_transaction_id_fkey", "cloud_invoice", type_="foreignkey")
    op.create_foreign_key(
        "cloud_invoice_transaction_id_fkey",
        "cloud_invoice",
        "ledger_transaction",
        ["transaction_id"],
        ["id"],
    )
