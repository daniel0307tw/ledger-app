from datetime import date

from sqlalchemy.orm import Session

from app.exceptions import InvalidParameterError
from app.models.ledger_transaction import LedgerTransaction
from app.repositories.transaction_repository import TransactionRepository


class ReportService:
    def __init__(self, session: Session):
        self.transactions = TransactionRepository(session)

    def get_category_summary(self, start_date: date, end_date: date) -> list[tuple[str, float]]:
        if start_date > end_date:
            raise InvalidParameterError("起始日期不可晚於結束日期")
        return self.transactions.sum_amount_by_category(start_date, end_date)

    def get_category_detail(self, category: str, start_date: date, end_date: date) -> list[LedgerTransaction]:
        if start_date > end_date:
            raise InvalidParameterError("起始日期不可晚於結束日期")
        return self.transactions.find_by_category_in_range(category, start_date, end_date)
