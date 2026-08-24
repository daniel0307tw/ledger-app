from behave import given

from app.models.account import AccountType
from app.repositories.account_repository import AccountRepository
from app.repositories.cash_position_repository import set_cash_position_db_path


@given("系統中有以下帳戶：")
def step_given_accounts(context):
    repo = AccountRepository(context.db_session)
    has_type_column = "type" in context.table.headings
    for row in context.table:
        account_type = AccountType(row["type"]) if has_type_column else AccountType.GENERAL
        account = repo.create(name=row["name"], type=account_type)
        context.accounts_by_name[row["name"]] = account
    context.db_session.commit()


@given("stock_analyzer 的資料庫暫時無法寫入")
def step_given_cash_position_unavailable(context):
    # 指向一個不存在的目錄，讓 CashPositionRepository 連線/寫入時失敗，
    # 模擬外部系統資料庫無法寫入的情境（例如檔案被鎖住）。
    set_cash_position_db_path("/nonexistent-directory-for-test/cash_position.db")
