from datetime import date

from sqlalchemy import and_, case, func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.ledger_transaction import AdvancePaymentStatus, LedgerTransaction, SyncStatus, TransactionType


def _effective_amount():
    """支出/預算/報表加總時實際計入的金額：已結清（advance_payment_amount 不為 null 且
    advance_payment_status=settled）的代墊款交易，有效金額為 amount − advance_payment_amount
    （而非排除整筆、也不是 0）；尚未結清或非代墊款交易仍以 amount 全額計入。"""
    return case(
        (
            and_(
                LedgerTransaction.advance_payment_amount.isnot(None),
                LedgerTransaction.advance_payment_status == AdvancePaymentStatus.SETTLED,
            ),
            LedgerTransaction.amount - LedgerTransaction.advance_payment_amount,
        ),
        else_=LedgerTransaction.amount,
    )


class TransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        date: date,
        amount,
        category_id: int | None,
        account_id: int,
        type: TransactionType,
        note: str | None = None,
        is_transfer: bool = False,
        transfer_group_id: str | None = None,
        sync_status: SyncStatus = SyncStatus.PENDING,
        cash_position_id: int | None = None,
        source_recurring_transaction_id: int | None = None,
        advance_payment_amount=None,
        advance_payment_status: AdvancePaymentStatus | None = None,
        settlement_transaction_id: int | None = None,
    ) -> LedgerTransaction:
        transaction = LedgerTransaction(
            date=date,
            amount=amount,
            category_id=category_id,
            account_id=account_id,
            type=type,
            note=note,
            is_transfer=is_transfer,
            transfer_group_id=transfer_group_id,
            sync_status=sync_status,
            cash_position_id=cash_position_id,
            source_recurring_transaction_id=source_recurring_transaction_id,
            advance_payment_amount=advance_payment_amount,
            advance_payment_status=advance_payment_status,
            settlement_transaction_id=settlement_transaction_id,
        )
        self.session.add(transaction)
        self.session.flush()
        return transaction

    def find(self, transaction_id: int) -> LedgerTransaction | None:
        return self.session.get(LedgerTransaction, transaction_id)

    def find_settlement_source(self, transaction_id: int) -> LedgerTransaction | None:
        """找出 settlement_transaction_id 指向 transaction_id 的那筆代墊款交易（若存在）。
        用於刪除「還款交易」時，回溯找出原代墊款交易以復原其結清狀態。"""
        return (
            self.session.query(LedgerTransaction)
            .filter(LedgerTransaction.settlement_transaction_id == transaction_id)
            .first()
        )

    def find_pending_advance_payments(self) -> list[LedgerTransaction]:
        return (
            self.session.query(LedgerTransaction)
            .filter(
                and_(
                    LedgerTransaction.advance_payment_amount.isnot(None),
                    LedgerTransaction.advance_payment_status == AdvancePaymentStatus.PENDING,
                )
            )
            .order_by(LedgerTransaction.date.desc(), LedgerTransaction.id.desc())
            .all()
        )

    def find_by_range(self, start_date: date, end_date: date) -> list[LedgerTransaction]:
        return (
            self.session.query(LedgerTransaction)
            .filter(and_(LedgerTransaction.date >= start_date, LedgerTransaction.date <= end_date))
            .order_by(LedgerTransaction.date.desc(), LedgerTransaction.id.desc())
            .all()
        )

    def find_by_date_and_amount(self, target_date: date, amount) -> LedgerTransaction | None:
        return (
            self.session.query(LedgerTransaction)
            .filter(
                and_(
                    LedgerTransaction.date == target_date,
                    LedgerTransaction.amount == amount,
                    LedgerTransaction.is_transfer.is_(False),
                )
            )
            .order_by(LedgerTransaction.id)
            .first()
        )

    def count_by_source_recurring_transaction(self, rule_id: int) -> int:
        return (
            self.session.query(LedgerTransaction)
            .filter(LedgerTransaction.source_recurring_transaction_id == rule_id)
            .count()
        )

    def find_by_source_recurring_transaction(self, rule_id: int) -> list[LedgerTransaction]:
        return (
            self.session.query(LedgerTransaction)
            .filter(LedgerTransaction.source_recurring_transaction_id == rule_id)
            .order_by(LedgerTransaction.date)
            .all()
        )

    def sum_amount_by_category_in_range(self, start_date: date, end_date: date) -> dict[int, float]:
        rows = (
            self.session.query(LedgerTransaction.category_id, func.sum(_effective_amount()))
            .filter(
                and_(
                    LedgerTransaction.date >= start_date,
                    LedgerTransaction.date <= end_date,
                    LedgerTransaction.type == TransactionType.EXPENSE,
                    LedgerTransaction.is_transfer.is_(False),
                )
            )
            .group_by(LedgerTransaction.category_id)
            .all()
        )
        return {category_id: float(total) for category_id, total in rows}

    def sum_amount_in_range(self, start_date: date, end_date: date) -> float:
        total = (
            self.session.query(func.sum(_effective_amount()))
            .filter(
                and_(
                    LedgerTransaction.date >= start_date,
                    LedgerTransaction.date <= end_date,
                    LedgerTransaction.type == TransactionType.EXPENSE,
                    LedgerTransaction.is_transfer.is_(False),
                )
            )
            .scalar()
        )
        return float(total) if total is not None else 0.0

    def delete(self, transaction: LedgerTransaction) -> None:
        self.session.delete(transaction)
        self.session.flush()

    def sum_balance_by_account(self) -> dict[int, float]:
        signed_amount = case(
            (LedgerTransaction.type == TransactionType.INCOME, LedgerTransaction.amount),
            else_=-LedgerTransaction.amount,
        )
        rows = (
            self.session.query(LedgerTransaction.account_id, func.sum(signed_amount))
            .group_by(LedgerTransaction.account_id)
            .all()
        )
        return {account_id: float(total) for account_id, total in rows}

    def find_by_category_in_range(
        self, category: str, start_date: date, end_date: date
    ) -> list[LedgerTransaction]:
        return (
            self.session.query(LedgerTransaction)
            .join(Category, LedgerTransaction.category_id == Category.id)
            .filter(
                and_(
                    Category.name == category,
                    LedgerTransaction.date >= start_date,
                    LedgerTransaction.date <= end_date,
                    LedgerTransaction.type == TransactionType.EXPENSE,
                    LedgerTransaction.is_transfer.is_(False),
                )
            )
            .order_by(LedgerTransaction.date.desc(), LedgerTransaction.id.desc())
            .all()
        )

    def sum_amount_by_category(self, start_date: date, end_date: date) -> list[tuple[str, float]]:
        rows = (
            self.session.query(Category.name, func.sum(_effective_amount()))
            .join(Category, LedgerTransaction.category_id == Category.id)
            .filter(
                and_(
                    LedgerTransaction.date >= start_date,
                    LedgerTransaction.date <= end_date,
                    LedgerTransaction.type == TransactionType.EXPENSE,
                    LedgerTransaction.is_transfer.is_(False),
                )
            )
            .group_by(Category.name)
            .order_by(func.sum(_effective_amount()).desc(), Category.name.asc())
            .all()
        )
        return [(name, float(total)) for name, total in rows]
