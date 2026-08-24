"""add cloud_invoice, recurring_transaction, budget tables; ledger_transaction.source_recurring_transaction_id

Revision ID: 004
Revises: 003
Create Date: 2026-08-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 不像既有 003 那樣先手動 .create(checkfirst=True) 再用——這裡的 enum 全部只在
    # create_table() 裡用一次，讓 create_table 自己順帶建立型別即可。若先手動建立、
    # 又在同一個 upgrade() 裡把同一個 Enum 物件放進 create_table，SQLAlchemy 會在
    # 編譯 CREATE TABLE DDL 時再嘗試建立一次同名型別（Enum 預設 create_type=True），
    # 導致 "type already exists" 錯誤——實測踩過這個坑，003 沒踩到是因為它只搭配
    # add_column，不是 create_table。
    cloud_invoice_status = sa.Enum("pending_review", "synced", "skipped", name="cloud_invoice_status")
    recurring_frequency = sa.Enum("每天", "每週", "每月", "每季", "每年", "每三年", name="recurring_frequency")
    recurring_transaction_status = sa.Enum("啟用", "停用", name="recurring_transaction_status")
    budget_scope = sa.Enum("總預算", "分類預算", name="budget_scope")

    op.create_table(
        "recurring_transaction",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("frequency", recurring_frequency, nullable=False),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("category.id"), nullable=False),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("account.id"), nullable=False),
        # 重用既有 transaction_type：用 postgresql.ENUM（非 sa.Enum）+ create_type=False。
        # 實測踩過的坑：plain sa.Enum(..., create_type=False) 在單獨執行本次 migration
        # （例如對已經跑過 001-003 的既有資料庫只補跑 004，而非從空庫一次跑完 001-004）
        # 時仍會嘗試 CREATE TYPE 並撞上 "already exists"——sa.Enum 對「這個型別是否該視為
        # 已存在」的判斷跟 metadata 綁定/同一連線快取有關，不是單看 create_type 這個旗標；
        # 換成 postgresql.ENUM 才會確實尊重 create_type=False。
        sa.Column(
            "type", PGEnum("收入", "支出", name="transaction_type", create_type=False), nullable=False
        ),
        sa.Column("note", sa.String, nullable=True),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("generate_count", sa.Integer, nullable=False),
        sa.Column("status", recurring_transaction_status, nullable=False, server_default="啟用"),
    )

    op.create_table(
        "cloud_invoice",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("invoice_number", sa.String, nullable=False, unique=True),
        sa.Column("invoice_date", sa.Date, nullable=False),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("seller_name", sa.String, nullable=False),
        sa.Column("item_summary", sa.String, nullable=True),
        sa.Column("status", cloud_invoice_status, nullable=False, server_default="pending_review"),
        sa.Column("transaction_id", sa.Integer, sa.ForeignKey("ledger_transaction.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "budget",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("scope", budget_scope, nullable=False),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("category.id"), nullable=True),
        sa.Column("monthly_amount", sa.Numeric(14, 4), nullable=False),
    )

    op.create_table(
        "cloud_invoice_sync_error",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("invoice_number", sa.String, nullable=True),
        sa.Column("error_message", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.add_column(
        "ledger_transaction",
        sa.Column(
            "source_recurring_transaction_id",
            sa.Integer,
            # ondelete=SET NULL：刪除規則時已生成的交易必須保留（Rule 已確認），
            # 沒有這個就會被 FK 擋下刪不掉規則（實測踩過）。
            sa.ForeignKey("recurring_transaction.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("ledger_transaction", "source_recurring_transaction_id")
    op.drop_table("cloud_invoice_sync_error")
    op.drop_table("budget")
    op.drop_table("cloud_invoice")
    op.drop_table("recurring_transaction")
    sa.Enum(name="budget_scope").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recurring_transaction_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="recurring_frequency").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="cloud_invoice_status").drop(op.get_bind(), checkfirst=True)
