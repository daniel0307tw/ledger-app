"""add is_stock_sync / currency to ledger_transaction

Revision ID: 007
Revises: 006
Create Date: 2026-09-16
"""

import sqlalchemy as sa

from alembic import op

revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ledger_transaction",
        sa.Column(
            "is_stock_sync", sa.Boolean, nullable=False, server_default=sa.false()
        ),
    )
    op.add_column(
        "ledger_transaction",
        sa.Column("currency", sa.String, nullable=False, server_default="TWD"),
    )


def downgrade() -> None:
    op.drop_column("ledger_transaction", "currency")
    op.drop_column("ledger_transaction", "is_stock_sync")
