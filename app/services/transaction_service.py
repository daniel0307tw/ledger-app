from datetime import date as date_type

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, InvalidParameterError, NotFoundError
from app.models.category import Category, CategoryType
from app.models.ledger_transaction import AdvancePaymentStatus, LedgerTransaction, TransactionType
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.cash_position_repository import CashPositionRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.cash_sync import cancel_previous_sync, sync_to_cash_position


def _assert_category_type_matches(category: Category, type: str) -> None:
    if category.type == CategoryType.BOTH:
        return
    if category.type.value != type:
        raise BusinessError("分類收支類型與交易類型不符")


def _decimal_or_none(value):
    return float(value) if value is not None else None


class TransactionService:
    def __init__(self, session: Session, cash_position_repository: CashPositionRepository | None = None):
        self.session = session
        self.accounts = AccountRepository(session)
        self.categories = CategoryRepository(session)
        self.transactions = TransactionRepository(session)
        self.cash_positions = cash_position_repository or CashPositionRepository()

    def create_transaction(
        self,
        *,
        date: date_type,
        amount,
        category_id: int,
        account_id: int,
        type: str,
        note: str | None = None,
        source_recurring_transaction_id: int | None = None,
        advance_payment_amount=None,
    ) -> LedgerTransaction:
        account = self.accounts.find(account_id)
        if account is None:
            raise NotFoundError("找不到該帳戶")
        category = self.categories.find(category_id)
        if category is None:
            raise NotFoundError("找不到該分類")
        # 這個檢查必須放在 _assert_category_type_matches 之前：Example「標記代墊款用於收入交易」
        # 用的分類（餐飲）本身是支出分類，若先做分類類型檢查會被「分類收支類型與交易類型不符」
        # 攔下，錯誤訊息就對不上規格要求的「代墊款標記僅限支出交易」。
        has_advance_payment = advance_payment_amount is not None
        if has_advance_payment and type != TransactionType.EXPENSE.value:
            raise BusinessError("代墊款標記僅限支出交易")
        if has_advance_payment and float(advance_payment_amount) > float(amount):
            raise BusinessError("代墊金額不可超過交易總金額")
        _assert_category_type_matches(category, type)

        transaction = self.transactions.create(
            date=date,
            amount=amount,
            category_id=category_id,
            account_id=account_id,
            type=TransactionType(type),
            note=note,
            source_recurring_transaction_id=source_recurring_transaction_id,
            advance_payment_amount=advance_payment_amount,
            advance_payment_status=AdvancePaymentStatus.PENDING if has_advance_payment else None,
        )
        sync_to_cash_position(self.cash_positions, transaction, institution=account.name)
        self.session.flush()
        return transaction

    def update_transaction(
        self,
        transaction_id: int,
        *,
        date: date_type,
        amount,
        category_id: int,
        account_id: int,
        type: str,
        note: str | None = None,
        advance_payment_amount=None,
    ) -> LedgerTransaction:
        transaction = self.transactions.find(transaction_id)
        if transaction is None:
            raise NotFoundError("找不到該筆收支紀錄")

        account = self.accounts.find(account_id)
        if account is None:
            raise NotFoundError("找不到該帳戶")
        category = self.categories.find(category_id)
        if category is None:
            raise NotFoundError("找不到該分類")
        has_advance_payment = advance_payment_amount is not None
        if has_advance_payment and type != TransactionType.EXPENSE.value:
            raise BusinessError("代墊款標記僅限支出交易")
        if has_advance_payment and float(advance_payment_amount) > float(amount):
            raise BusinessError("代墊金額不可超過交易總金額")
        _assert_category_type_matches(category, type)

        cancel_previous_sync(self.cash_positions, transaction)

        was_settled = transaction.advance_payment_status == AdvancePaymentStatus.SETTLED
        original_amount = transaction.amount
        original_advance_payment_amount = transaction.advance_payment_amount

        transaction.date = date
        transaction.amount = amount
        transaction.category_id = category_id
        transaction.account_id = account_id
        transaction.type = TransactionType(type)
        transaction.note = note
        transaction.advance_payment_amount = advance_payment_amount

        # 編輯一筆已結清的代墊款交易，若總金額或代墊金額任一變動，代表原本核對過的還款金額
        # 已不再成立：自動改回未結清並解除與還款交易的關聯（該筆還款收入交易本身不連動變更）。
        # 非已結清狀態（含本來就沒有代墊款、或本來已是未結清）則直接依新的 advance_payment_amount
        # 重新決定狀態——涵蓋「編輯時才第一次加上代墊金額」這種原本漏處理、狀態停留在 null 導致
        # 不會出現在待收回代墊款清單的情況。
        amount_changed = float(amount) != float(original_amount)
        advance_payment_amount_changed = _decimal_or_none(advance_payment_amount) != _decimal_or_none(
            original_advance_payment_amount
        )
        if not was_settled or amount_changed or advance_payment_amount_changed:
            transaction.advance_payment_status = AdvancePaymentStatus.PENDING if has_advance_payment else None
            if was_settled:
                transaction.settlement_transaction_id = None

        sync_to_cash_position(self.cash_positions, transaction, institution=account.name)
        self.session.flush()
        return transaction

    def delete_transaction(self, transaction_id: int) -> None:
        transaction = self.transactions.find(transaction_id)
        if transaction is None:
            raise NotFoundError("找不到該筆收支紀錄")

        cancel_previous_sync(self.cash_positions, transaction)

        # 若這筆是某筆代墊款交易的「還款交易」，刪除前先解除對方的關聯、復原為未結清，
        # 避免刪除本筆時撞上 settlement_transaction_id 的 FK（雖然該 FK 已設 ON DELETE SET NULL
        # 作為額外防線，這裡明確處理是為了同時把 advance_payment_status 復原）。
        settlement_source = self.transactions.find_settlement_source(transaction_id)
        if settlement_source is not None:
            settlement_source.advance_payment_status = AdvancePaymentStatus.PENDING
            settlement_source.settlement_transaction_id = None
            self.session.flush()

        self.transactions.delete(transaction)

    def list_transactions(self, start_date: date_type, end_date: date_type) -> list[LedgerTransaction]:
        if start_date > end_date:
            raise InvalidParameterError("起始日期不可晚於結束日期")
        return self.transactions.find_by_range(start_date, end_date)

    def settle_advance_payment(
        self,
        transaction_id: int,
        *,
        date: date_type,
        amount,
        account_id: int,
    ) -> tuple[LedgerTransaction, LedgerTransaction]:
        transaction = self.transactions.find(transaction_id)
        if transaction is None:
            raise NotFoundError("找不到該筆收支紀錄")
        if transaction.advance_payment_amount is None:
            raise BusinessError("該筆交易非代墊款交易")
        if transaction.advance_payment_status == AdvancePaymentStatus.SETTLED:
            raise BusinessError("該筆代墊款已結清")
        if float(amount) != float(transaction.advance_payment_amount):
            raise BusinessError("還款金額與代墊金額不符，僅支援全額還款")
        account = self.accounts.find(account_id)
        if account is None:
            raise NotFoundError("找不到該帳戶")

        # 比照 TransferService.create_transfer 的作法：直接透過 repository 建立這筆還款收入交易
        # （category_id=None——這筆錢的分類意義不明確，非一般收支紀錄，比照轉帳紀錄的既有慣例），
        # 而非呼叫 create_transaction()（那個入口會強制要求 categoryId，不適用於這裡）。
        settlement_transaction = self.transactions.create(
            date=date,
            amount=amount,
            category_id=None,
            account_id=account_id,
            type=TransactionType.INCOME,
        )
        sync_to_cash_position(self.cash_positions, settlement_transaction, institution=account.name)

        transaction.advance_payment_status = AdvancePaymentStatus.SETTLED
        transaction.settlement_transaction_id = settlement_transaction.id

        self.session.flush()
        return settlement_transaction, transaction

    def list_pending_advance_payments(self) -> list[LedgerTransaction]:
        return self.transactions.find_pending_advance_payments()
