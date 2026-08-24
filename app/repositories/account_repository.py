from sqlalchemy.orm import Session

from app.models.account import Account, AccountType


class AccountRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, name: str, type: AccountType) -> Account:
        account = Account(name=name, type=type)
        self.session.add(account)
        self.session.flush()
        return account

    def find(self, account_id: int) -> Account | None:
        return self.session.get(Account, account_id)

    def find_all(self) -> list[Account]:
        return self.session.query(Account).order_by(Account.id).all()

    def find_by_name(self, name: str) -> Account | None:
        # .first()（非 one_or_none）：account.name 同樣不強制唯一，理由同 CategoryRepository.find_by_name。
        return self.session.query(Account).filter(Account.name == name).order_by(Account.id).first()
