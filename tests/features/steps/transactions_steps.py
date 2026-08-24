import re
import sqlite3
from datetime import date
from decimal import Decimal

from behave import given, then, use_step_matcher, when

from app.models.ledger_transaction import AdvancePaymentStatus, LedgerTransaction, SyncStatus, TransactionType
from app.repositories.cash_position_repository import CashPositionRepository
from app.repositories.transaction_repository import TransactionRepository

_REF_PATTERN = re.compile(r"^\$收支紀錄(\d+)\.id$")
_NONEXISTENT_ID_SENTINEL = 999999999
_NONEXISTENT_ACCOUNT_NAME = "不存在的帳戶"
_NONEXISTENT_CATEGORY_NAME = "不存在的分類"


def resolve_transaction_ref(context, ref: str) -> int:
    """把 Gherkin 裡的交易參照解析成實際的資料庫 id。

    支援三種寫法：
    - `$收支紀錄1.id`：查表格宣告的 id "1" 對應到的真實 DB id
    - 純數字字串：直接當 id
    - 其他（如引號包住的 business-readable 佔位字串「不存在的id」）：視為刻意不存在的 sentinel id
    """
    ref = ref.strip()
    if ref.startswith('"') and ref.endswith('"'):
        ref = ref[1:-1]
    match = _REF_PATTERN.match(ref)
    if match:
        return context.ids[match.group(1)]
    if ref.isdigit():
        return int(ref)
    return _NONEXISTENT_ID_SENTINEL


@given("系統中有以下收支紀錄：")
def step_given_transactions(context):
    repo = TransactionRepository(context.db_session)
    cash_positions = CashPositionRepository()
    has_sync_status_column = "sync_status" in context.table.headings
    has_advance_payment_column = "advancePaymentAmount" in context.table.headings
    has_advance_payment_status_column = "advancePaymentStatus" in context.table.headings
    has_settlement_column = "settlementTransactionId" in context.table.headings
    has_note_column = "note" in context.table.headings
    for row in context.table:
        account = context.accounts_by_name[row["account"]]
        sync_status = SyncStatus(row["sync_status"]) if has_sync_status_column else SyncStatus.PENDING
        cash_position_id = None
        if sync_status == SyncStatus.SYNCED:
            cash_type = "Withdraw" if row["type"] == TransactionType.EXPENSE.value else "Deposit"
            cash_position_id = cash_positions.create(
                institution=account.name, amount=Decimal(row["amount"]), currency="TWD", type=cash_type
            )
        category = context.categories_by_name[row["category"]]
        advance_payment_amount = None
        if has_advance_payment_column and row["advancePaymentAmount"].strip():
            advance_payment_amount = Decimal(row["advancePaymentAmount"].strip())
        advance_payment_status = None
        if has_advance_payment_status_column and row["advancePaymentStatus"].strip():
            advance_payment_status = AdvancePaymentStatus(row["advancePaymentStatus"].strip())
        settlement_transaction_id = None
        if has_settlement_column and row["settlementTransactionId"].strip():
            settlement_transaction_id = resolve_transaction_ref(context, row["settlementTransactionId"])
        note = row["note"].strip() or None if has_note_column else None
        transaction = repo.create(
            date=date.fromisoformat(row["date"]),
            amount=Decimal(row["amount"]),
            category_id=category.id,
            account_id=account.id,
            type=TransactionType(row["type"]),
            note=note,
            sync_status=sync_status,
            cash_position_id=cash_position_id,
            advance_payment_amount=advance_payment_amount,
            advance_payment_status=advance_payment_status,
            settlement_transaction_id=settlement_transaction_id,
        )
        context.ids[row["id"]] = transaction.id
        if cash_position_id is not None:
            context.memo[f"cash_position_id_for_{transaction.id}"] = cash_position_id
    context.db_session.commit()


@when("使用者建立收支紀錄：")
def step_when_create_transaction(context):
    row = context.table[0]
    payload = {}
    if row["date"]:
        payload["date"] = row["date"]
    if row["amount"] != "":
        payload["amount"] = float(row["amount"])
    if row["category"] == _NONEXISTENT_CATEGORY_NAME:
        payload["categoryId"] = _NONEXISTENT_ID_SENTINEL
    elif row["category"]:
        payload["categoryId"] = context.categories_by_name[row["category"]].id
    if row["account"] == _NONEXISTENT_ACCOUNT_NAME:
        payload["accountId"] = _NONEXISTENT_ID_SENTINEL
    elif row["account"]:
        payload["accountId"] = context.accounts_by_name[row["account"]].id
    if row["type"]:
        payload["type"] = row["type"]
    if "note" in context.table.headings and row["note"]:
        payload["note"] = row["note"]
    if "advancePaymentAmount" in context.table.headings and row["advancePaymentAmount"].strip():
        payload["advancePaymentAmount"] = float(row["advancePaymentAmount"].strip())

    context.last_response = context.api_client.post("/api/transactions", json=payload)
    body = context.last_response.json()
    if body.get("success"):
        context.ids["__last_created__"] = body["data"]["id"]


@when("使用者編輯收支紀錄 {ref}：")
def step_when_edit_transaction(context, ref):
    transaction_id = resolve_transaction_ref(context, ref)
    row = context.table[0]
    payload = {
        "date": row["date"],
        "amount": float(row["amount"]),
        "categoryId": context.categories_by_name[row["category"]].id,
        "accountId": context.accounts_by_name[row["account"]].id,
        "type": row["type"],
    }
    if "advancePaymentAmount" in context.table.headings and row["advancePaymentAmount"].strip():
        payload["advancePaymentAmount"] = float(row["advancePaymentAmount"].strip())
    context.last_response = context.api_client.put(f"/api/transactions/{transaction_id}", json=payload)


@when("使用者刪除收支紀錄 {ref}")
def step_when_delete_transaction(context, ref):
    transaction_id = resolve_transaction_ref(context, ref)
    context.last_response = context.api_client.delete(f"/api/transactions/{transaction_id}")


@when("使用者對收支紀錄 {ref} 確認收到還款：")
def step_when_settle_advance_payment(context, ref):
    transaction_id = resolve_transaction_ref(context, ref)
    row = context.table[0]
    payload = {}
    if row["date"]:
        payload["date"] = row["date"]
    if row["amount"] != "":
        payload["amount"] = float(row["amount"])
    if row["account"] == _NONEXISTENT_ACCOUNT_NAME:
        payload["accountId"] = _NONEXISTENT_ID_SENTINEL
    elif row["account"]:
        payload["accountId"] = context.accounts_by_name[row["account"]].id

    context.last_response = context.api_client.post(
        f"/api/transactions/{transaction_id}/settle-advance-payment", json=payload
    )


@when("使用者查詢待收回代墊款清單")
def step_when_query_pending_advance_payments(context):
    context.last_response = context.api_client.get("/api/transactions/pending-advance-payments")


# parse 的 {name} 佔位符預設要求至少 1 個字元，無法匹配 Outline substitution 出的空字串
# （模擬「缺少查詢參數」時 start_date/end_date 會被替換成空字串），故這一條改用正規表示式比對。
use_step_matcher("re")


@when(r"使用者查詢收支紀錄，起始日期 (?P<start_date>.*?) 結束日期 (?P<end_date>.*)")
def step_when_query_transactions(context, start_date, end_date):
    params = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    context.last_response = context.api_client.get("/api/transactions", params=params)


use_step_matcher("parse")


@then("操作成功，結果符合：")
def step_then_result_matches(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    expected = context.table[0]
    data = resp["data"]
    for heading in context.table.headings:
        expected_value = expected[heading]
        if heading == "account":
            expected_account_id = context.accounts_by_name[expected_value].id
            assert data.get("accountId") == expected_account_id, (
                f"accountId: expected {expected_account_id}, got {data.get('accountId')}"
            )
        elif heading == "category":
            expected_category_id = context.categories_by_name[expected_value].id
            assert data.get("categoryId") == expected_category_id, (
                f"categoryId: expected {expected_category_id}, got {data.get('categoryId')}"
            )
        elif heading == "amount":
            assert float(data.get("amount")) == float(expected_value), (
                f"amount: expected {expected_value}, got {data.get('amount')}"
            )
        elif heading == "advancePaymentAmount":
            expected_amount = float(expected_value) if expected_value.strip() else None
            actual_amount = data.get("advancePaymentAmount")
            actual_amount = float(actual_amount) if actual_amount is not None else None
            assert actual_amount == expected_amount, (
                f"advancePaymentAmount: expected {expected_amount}, got {actual_amount}"
            )
        else:
            assert str(data.get(heading)) == expected_value, (
                f"{heading}: expected {expected_value}, got {data.get(heading)}"
            )


@then("應建立一筆收支紀錄：")
def step_then_transaction_created(context):
    resp = context.last_response.json()
    assert resp.get("success") is True
    expected = context.table[0]
    data = resp["data"]
    # 「確認收到還款」的回應是 { settlementTransaction, advancePaymentTransaction } 的巢狀結構
    # （非單一 Transaction），這裡取新建立的還款交易來比對。
    if "settlementTransaction" in data:
        data = data["settlementTransaction"]
    assert data["date"] == expected["date"]
    assert float(data["amount"]) == float(expected["amount"])
    if "category" in context.table.headings:
        assert data["categoryId"] == context.categories_by_name[expected["category"]].id
    assert data["type"] == expected["type"]
    assert data["accountId"] == context.accounts_by_name[expected["account"]].id


@then('收支紀錄 {ref} 的代墊款狀態應為 "{status}"')
def step_then_advance_payment_status(context, ref, status):
    transaction_id = resolve_transaction_ref(context, ref)
    context.db_session.expire_all()
    transaction = context.db_session.get(LedgerTransaction, transaction_id)
    assert transaction.advance_payment_status.value == status, (
        f"Expected advance_payment_status={status}, got {transaction.advance_payment_status}"
    )


@then("操作成功，查詢結果應包含以下待收回代墊款：")
def step_then_pending_advance_payments(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]

    expected = {
        (
            row["date"],
            float(row["amount"]),
            context.categories_by_name[row["category"]].id,
            context.accounts_by_name[row["account"]].id,
            float(row["advancePaymentAmount"]) if row["advancePaymentAmount"].strip() else None,
        )
        for row in context.table
    }
    actual = {
        (
            item["date"],
            float(item["amount"]),
            item["categoryId"],
            item["accountId"],
            float(item["advancePaymentAmount"]) if item.get("advancePaymentAmount") is not None else None,
        )
        for item in data
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


@then("收支紀錄 {ref} 應不存在")
def step_then_transaction_not_exist(context, ref):
    transaction_id = resolve_transaction_ref(context, ref)
    context.db_session.expire_all()
    found = context.db_session.get(LedgerTransaction, transaction_id)
    assert found is None, f"Expected transaction {transaction_id} to be deleted, still found: {found}"


@then('收支紀錄的同步狀態應為 "{status}"')
def step_then_last_created_sync_status(context, status):
    transaction_id = context.ids["__last_created__"]
    context.db_session.expire_all()
    transaction = context.db_session.get(LedgerTransaction, transaction_id)
    assert transaction.sync_status.value == status, f"Expected sync_status={status}, got {transaction.sync_status}"


@then('收支紀錄 {ref} 的同步狀態應為 "{status}"')
def step_then_ref_sync_status(context, ref, status):
    transaction_id = resolve_transaction_ref(context, ref)
    context.db_session.expire_all()
    transaction = context.db_session.get(LedgerTransaction, transaction_id)
    assert transaction.sync_status.value == status, f"Expected sync_status={status}, got {transaction.sync_status}"


def _read_cash_positions(context):
    conn = sqlite3.connect(context.cash_position_db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM cash_position").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _assert_cash_position_row_exists(rows, expected):
    match = [
        r
        for r in rows
        if r["institution"] == expected["institution"]
        and r["type"] == expected["type"]
        and str(r["currency"]) == expected["currency"]
        and float(r["amount"]) == float(expected["amount"])
    ]
    assert match, f"Expected a CashPosition row matching {dict(expected)}, got {rows}"


@then("stock_analyzer 的 CashPosition 應新增一筆：")
def step_then_cash_position_created(context):
    rows = _read_cash_positions(context)
    _assert_cash_position_row_exists(rows, context.table[0])


@then("stock_analyzer 的 CashPosition 應新增兩筆：")
def step_then_cash_position_created_two(context):
    rows = _read_cash_positions(context)
    for expected in context.table:
        _assert_cash_position_row_exists(rows, expected)


@then("stock_analyzer 的 CashPosition 不應再包含收支紀錄 {ref} 對應的那筆")
def step_then_cash_position_removed(context, ref):
    transaction_id = resolve_transaction_ref(context, ref)
    cash_position_id = context.memo.get(f"cash_position_id_for_{transaction_id}")
    assert cash_position_id is not None, f"No cash_position_id recorded for transaction {transaction_id}"
    rows = _read_cash_positions(context)
    ids = {r["id"] for r in rows}
    assert cash_position_id not in ids, f"Expected cash_position {cash_position_id} to be removed, still present"


@then("操作成功，查詢結果應包含：")
def step_then_query_contains(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    expected_rows = list(context.table)
    assert len(data) == len(expected_rows), f"Expected {len(expected_rows)} rows, got {len(data)}: {data}"

    if "date" in context.table.headings:
        for expected, actual in zip(expected_rows, data):
            assert actual["date"] == expected["date"]
            assert float(actual["amount"]) == float(expected["amount"])
            assert actual["categoryId"] == context.categories_by_name[expected["category"]].id
            assert actual["type"] == expected["type"]
    elif "balance" in context.table.headings:
        expected_set = {(row["name"], row["type"], float(row["balance"])) for row in expected_rows}
        actual_set = {(item["name"], item["type"], float(item["balance"])) for item in data}
        assert expected_set == actual_set, f"Expected accounts {expected_set}, got {actual_set}"
    elif "type" in context.table.headings:
        expected_set = {(row["name"], row["type"]) for row in expected_rows}
        actual_set = {(item["name"], item["type"]) for item in data}
        assert expected_set == actual_set, f"Expected categories {expected_set}, got {actual_set}"
    else:
        expected_names = {row["name"] for row in expected_rows}
        actual_names = {item["name"] for item in data}
        assert expected_names == actual_names, f"Expected names {expected_names}, got {actual_names}"
