"""create account and ledger_transaction

Revision ID: 001
Revises:
Create Date: 2026-08-23
"""

import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "account",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
    )

    transaction_type = sa.Enum("收入", "支出", name="transaction_type")
    sync_status_enum = sa.Enum("pending", "synced", "failed", name="sync_status_enum")

    op.create_table(
        "ledger_transaction",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("amount", sa.Numeric(14, 4), nullable=False),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("note", sa.String, nullable=True),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("account.id"), nullable=False),
        sa.Column("type", transaction_type, nullable=False),
        sa.Column("is_transfer", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("transfer_group_id", sa.String, nullable=True),
        sa.Column("sync_status", sync_status_enum, nullable=False, server_default="pending"),
        sa.Column("cash_position_id", sa.Integer, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("ledger_transaction")
    op.drop_table("account")
    sa.Enum(name="transaction_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="sync_status_enum").drop(op.get_bind(), checkfirst=True)
