"""add category table, replace ledger_transaction.category with category_id

Revision ID: 002
Revises: 001
Create Date: 2026-08-23
"""

import sqlalchemy as sa
from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None

DEFAULT_CATEGORIES = [
    "餐飲",
    "日常用品",
    "交通",
    "水電瓦斯",
    "電話網路",
    "居家",
    "服飾",
    "汽車",
    "娛樂",
    "美容美髮",
    "交際應酬",
    "學習深造",
    "保險",
    "稅金",
    "醫療",
    "校正回歸",
    "轉帳手續費",
]


def upgrade() -> None:
    category_table = op.create_table(
        "category",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
    )

    op.bulk_insert(category_table, [{"name": name} for name in DEFAULT_CATEGORIES])

    op.drop_column("ledger_transaction", "category")
    op.add_column(
        "ledger_transaction",
        sa.Column("category_id", sa.Integer, sa.ForeignKey("category.id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("ledger_transaction", "category_id")
    op.add_column("ledger_transaction", sa.Column("category", sa.String, nullable=False, server_default=""))
    op.drop_table("category")
