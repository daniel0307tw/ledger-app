"""add advance_payment_amount / advance_payment_status / settlement_transaction_id to ledger_transaction

Revision ID: 006
Revises: 005
Create Date: 2026-08-24
"""

import sqlalchemy as sa
from alembic import op

revision = "006"
down_revision = "005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 比照既有 003 的手法：先手動 create(checkfirst=True) 建立型別，再把同一個 Enum 物件
    # 傳給 add_column——這裡是 ADD COLUMN 而非 create_table，不會撞上 004 註解描述的
    # "type already exists" 問題（那個坑只發生在 create_table 內同時使用同一個 Enum 物件時）。
    advance_payment_status_enum = sa.Enum("pending", "settled", name="advance_payment_status_enum")
    bind = op.get_bind()
    advance_payment_status_enum.create(bind, checkfirst=True)

    op.add_column(
        "ledger_transaction",
        sa.Column("advance_payment_amount", sa.Numeric(14, 4), nullable=True),
    )
    op.add_column(
        "ledger_transaction",
        sa.Column("advance_payment_status", advance_payment_status_enum, nullable=True),
    )
    op.add_column(
        "ledger_transaction",
        sa.Column(
            "settlement_transaction_id",
            sa.Integer,
            # ondelete=SET NULL：比照 source_recurring_transaction_id 的既有設計，讓刪除
            # 「還款交易」時不會被 FK 擋下（service 層另外手動處理狀態復原，這裡是額外防線）。
            sa.ForeignKey("ledger_transaction.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("ledger_transaction", "settlement_transaction_id")
    op.drop_column("ledger_transaction", "advance_payment_status")
    op.drop_column("ledger_transaction", "advance_payment_amount")
    sa.Enum(name="advance_payment_status_enum").drop(op.get_bind(), checkfirst=True)
