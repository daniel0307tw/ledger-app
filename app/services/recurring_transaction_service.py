import calendar
from datetime import date as date_type
from datetime import timedelta

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.ledger_transaction import LedgerTransaction, TransactionType
from app.models.recurring_transaction import RecurringFrequency, RecurringTransaction, RecurringTransactionStatus
from app.repositories.recurring_transaction_repository import RecurringTransactionRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.transaction_service import TransactionService


def _add_months(d: date_type, months: int) -> date_type:
    """加上整數個月，日期溢位時夾到目標月份的最後一天（例如 1/31 加 1 個月 → 2/28）。
    只用標準庫，不引入 python-dateutil 這個新依賴——月/季/年/三年都能用這支函式組合表達。"""
    total_month_index = d.month - 1 + months
    year = d.year + total_month_index // 12
    month = total_month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date_type(year, month, day)


_FREQUENCY_STEP = {
    RecurringFrequency.DAILY: lambda d: d + timedelta(days=1),
    RecurringFrequency.WEEKLY: lambda d: d + timedelta(weeks=1),
    RecurringFrequency.MONTHLY: lambda d: _add_months(d, 1),
    RecurringFrequency.QUARTERLY: lambda d: _add_months(d, 3),
    RecurringFrequency.YEARLY: lambda d: _add_months(d, 12),
    RecurringFrequency.TRIENNIAL: lambda d: _add_months(d, 36),
}


class RecurringTransactionService:
    def __init__(self, session: Session):
        self.session = session
        self.rules = RecurringTransactionRepository(session)
        self.transactions = TransactionRepository(session)
        self.transaction_service = TransactionService(session)

    def _generate_dates(self, rule: RecurringTransaction, count: int, skip: int) -> list[date_type]:
        step = _FREQUENCY_STEP[RecurringFrequency(rule.frequency)]
        dates = []
        current = rule.start_date
        for i in range(skip + count):
            if i >= skip:
                dates.append(current)
            current = step(current)
        return dates

    def _create_transactions_for_rule(self, rule: RecurringTransaction, count: int, skip: int) -> list[LedgerTransaction]:
        dates = self._generate_dates(rule, count, skip)
        created = []
        for occurrence_date in dates:
            transaction = self.transaction_service.create_transaction(
                date=occurrence_date,
                amount=rule.amount,
                category_id=rule.category_id,
                account_id=rule.account_id,
                type=rule.type.value,
                note=rule.note,
                source_recurring_transaction_id=rule.id,
            )
            created.append(transaction)
        return created

    def create_rule(
        self,
        *,
        frequency: str,
        amount,
        category_id: int,
        account_id: int,
        type: str,
        note: str | None,
        start_date: date_type,
        generate_count: int,
    ) -> tuple[RecurringTransaction, list[LedgerTransaction]]:
        rule = self.rules.create(
            frequency=RecurringFrequency(frequency),
            amount=amount,
            category_id=category_id,
            account_id=account_id,
            type=TransactionType(type),
            note=note,
            start_date=start_date,
            generate_count=generate_count,
        )
        created = self._create_transactions_for_rule(rule, generate_count, skip=0)
        self.session.flush()
        return rule, created

    def update_rule(
        self,
        rule_id: int,
        *,
        frequency: str,
        amount,
        category_id: int,
        account_id: int,
        type: str,
        note: str | None,
        start_date: date_type,
        generate_count: int,
    ) -> RecurringTransaction:
        rule = self.rules.find(rule_id)
        if rule is None:
            raise NotFoundError("找不到該固定收支規則")
        rule.frequency = RecurringFrequency(frequency)
        rule.amount = amount
        rule.category_id = category_id
        rule.account_id = account_id
        rule.type = TransactionType(type)
        rule.note = note
        rule.start_date = start_date
        rule.generate_count = generate_count
        self.session.flush()
        return rule

    def delete_rule(self, rule_id: int) -> None:
        rule = self.rules.find(rule_id)
        if rule is None:
            raise NotFoundError("找不到該固定收支規則")
        self.rules.delete(rule)

    def list_rules(self) -> list[RecurringTransaction]:
        return self.rules.find_all()

    def generate(self, rule_id: int) -> list[LedgerTransaction]:
        rule = self.rules.find(rule_id)
        if rule is None:
            raise NotFoundError("找不到該固定收支規則")
        if rule.status != RecurringTransactionStatus.ENABLED:
            return []
        already_generated = self.transactions.count_by_source_recurring_transaction(rule_id)
        missing = rule.generate_count - already_generated
        if missing <= 0:
            return []
        created = self._create_transactions_for_rule(rule, missing, skip=already_generated)
        self.session.flush()
        return created
