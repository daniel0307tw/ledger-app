"""add category.type and account.type, seed income categories

Revision ID: 003
Revises: 002
Create Date: 2026-08-23
"""

import sqlalchemy as sa
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None

NEW_INCOME_CATEGORIES = ["薪資", "獎金", "投資"]
BOTH_TYPE_CATEGORY = "校正回歸"


def upgrade() -> None:
    category_type = sa.Enum("收入", "支出", "皆可", name="category_type")
    account_type = sa.Enum("一般帳戶", "信用卡", name="account_type")
    bind = op.get_bind()
    category_type.create(bind, checkfirst=True)
    account_type.create(bind, checkfirst=True)

    op.add_column("category", sa.Column("type", category_type, nullable=True))
    op.execute(
        sa.text("UPDATE category SET type = '支出' WHERE name != :both").bindparams(both=BOTH_TYPE_CATEGORY)
    )
    op.execute(
        sa.text("UPDATE category SET type = '皆可' WHERE name = :both").bindparams(both=BOTH_TYPE_CATEGORY)
    )
    op.alter_column("category", "type", nullable=False)

    category_table = sa.table("category", sa.column("name", sa.String), sa.column("type", category_type))
    op.bulk_insert(category_table, [{"name": name, "type": "收入"} for name in NEW_INCOME_CATEGORIES])

    op.add_column("account", sa.Column("type", account_type, nullable=True))
    op.execute(sa.text("UPDATE account SET type = '一般帳戶'"))
    op.alter_column("account", "type", nullable=False)


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM category WHERE name = ANY(:names)").bindparams(names=NEW_INCOME_CATEGORIES)
    )
    op.drop_column("account", "type")
    op.drop_column("category", "type")
    sa.Enum(name="account_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="category_type").drop(op.get_bind(), checkfirst=True)
