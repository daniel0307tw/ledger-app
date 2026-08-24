import uuid
from datetime import date as date_type

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.ledger_transaction import LedgerTransaction, TransactionType
from app.repositories.account_repository import AccountRepository
from app.repositories.cash_position_repository import CashPositionRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.cash_sync import sync_to_cash_position


class TransferService:
    def __init__(self, session: Session, cash_position_repository: CashPositionRepository | None = None):
        self.session = session
        self.accounts = AccountRepository(session)
        self.transactions = TransactionRepository(session)
        self.cash_positions = cash_position_repository or CashPositionRepository()

    def create_transfer(
        self, *, from_account_id: int, to_account_id: int, amount, date: date_type
    ) -> tuple[LedgerTransaction, LedgerTransaction]:
        from_account = self.accounts.find(from_account_id)
        if from_account is None:
            raise NotFoundError("找不到該帳戶")
        to_account = self.accounts.find(to_account_id)
        if to_account is None:
            raise NotFoundError("找不到該帳戶")
        if from_account_id == to_account_id:
            raise BusinessError("轉出帳戶與轉入帳戶不可相同")

        transfer_group_id = str(uuid.uuid4())

        outgoing = self.transactions.create(
            date=date,
            amount=amount,
            category_id=None,
            account_id=from_account_id,
            type=TransactionType.EXPENSE,
            is_transfer=True,
            transfer_group_id=transfer_group_id,
        )
        incoming = self.transactions.create(
            date=date,
            amount=amount,
            category_id=None,
            account_id=to_account_id,
            type=TransactionType.INCOME,
            is_transfer=True,
            transfer_group_id=transfer_group_id,
        )

        sync_to_cash_position(self.cash_positions, outgoing, institution=from_account.name)
        sync_to_cash_position(self.cash_positions, incoming, institution=to_account.name)
        self.session.flush()

        return outgoing, incoming
