from sqlalchemy.orm import Session

from app.models.account import AccountType
from app.repositories.account_repository import AccountRepository
from app.repositories.transaction_repository import TransactionRepository


class AccountService:
    def __init__(self, session: Session):
        self.repository = AccountRepository(session)
        self.transactions = TransactionRepository(session)

    def create_account(self, name: str, type: AccountType) -> dict:
        account = self.repository.create(name=name, type=type)
        return {"id": account.id, "name": account.name, "type": account.type, "balance": 0.0}

    def list_accounts(self) -> list[dict]:
        accounts = self.repository.find_all()
        balances = self.transactions.sum_balance_by_account()
        return [
            {
                "id": account.id,
                "name": account.name,
                "type": account.type,
                "balance": balances.get(account.id, 0.0),
            }
            for account in accounts
        ]
