from datetime import date

from sqlalchemy.orm import Session

from app.models.recurring_transaction import RecurringFrequency, RecurringTransaction, RecurringTransactionStatus


class RecurringTransactionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        frequency: RecurringFrequency,
        amount,
        category_id: int,
        account_id: int,
        type,
        note: str | None = None,
        start_date: date,
        generate_count: int,
        status: RecurringTransactionStatus = RecurringTransactionStatus.ENABLED,
    ) -> RecurringTransaction:
        rule = RecurringTransaction(
            frequency=frequency,
            amount=amount,
            category_id=category_id,
            account_id=account_id,
            type=type,
            note=note,
            start_date=start_date,
            generate_count=generate_count,
            status=status,
        )
        self.session.add(rule)
        self.session.flush()
        return rule

    def find(self, rule_id: int) -> RecurringTransaction | None:
        return self.session.get(RecurringTransaction, rule_id)

    def find_all(self) -> list[RecurringTransaction]:
        return self.session.query(RecurringTransaction).order_by(RecurringTransaction.id).all()

    def delete(self, rule: RecurringTransaction) -> None:
        self.session.delete(rule)
        self.session.flush()
