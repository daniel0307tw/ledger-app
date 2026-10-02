from datetime import date as date_type

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.ledger_transaction import LedgerTransaction, TransactionType
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository

# 本 service 刻意獨立於 TransactionService/TransferService 之外（比照既有 TransferService
# 的獨立模式）：is_stock_sync=true 的交易絕不觸發既有的 sync_to_cash_position() /
# cancel_previous_sync()——stock_analyzer 已經在它自己那邊寫過對應的 cash_position，
# 若這裡又反向同步一次，現金會被重複計算（見 plans/接收股票交易現金異動/execution-plan.md）。


class StockSyncService:
    def __init__(self, session: Session):
        self.session = session
        self.accounts = AccountRepository(session)
        self.transactions = TransactionRepository(session)

    def create_stock_sync_transaction(
        self, *, direction: str, amount, currency: str, account_name: str
    ) -> LedgerTransaction:
        account = self.accounts.find_by_name(account_name)
        if account is None:
            raise NotFoundError("找不到該帳戶")

        transaction = self.transactions.create(
            date=date_type.today(),
            amount=amount,
            category_id=None,
            account_id=account.id,
            type=TransactionType(direction),
            is_transfer=True,
            is_stock_sync=True,
            currency=currency,
        )
        self.session.flush()
        return transaction

    def _find_stock_sync_transaction(self, transaction_id: int) -> LedgerTransaction:
        transaction = self.transactions.find(transaction_id)
        if transaction is None or not transaction.is_stock_sync:
            raise NotFoundError("找不到該筆收支紀錄")
        return transaction

    def update_stock_sync_transaction(
        self, transaction_id: int, *, amount, direction: str
    ) -> LedgerTransaction:
        transaction = self._find_stock_sync_transaction(transaction_id)
        transaction.amount = amount
        transaction.type = TransactionType(direction)
        self.session.flush()
        return transaction

    def delete_stock_sync_transaction(self, transaction_id: int) -> None:
        transaction = self._find_stock_sync_transaction(transaction_id)
        self.transactions.delete(transaction)
