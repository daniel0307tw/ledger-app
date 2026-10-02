import re
import sqlite3
from datetime import date
from decimal import Decimal

from behave import given, then, when

from app.models.ledger_transaction import LedgerTransaction, TransactionType
from app.repositories.transaction_repository import TransactionRepository

_REF_PATTERN = re.compile(r"^\$收支紀錄(\d+)\.id$")
_NONEXISTENT_ID_SENTINEL = 999999999


def _resolve_ref(context, ref: str) -> int:
    ref = ref.strip()
    if ref.startswith('"') and ref.endswith('"'):
        ref = ref[1:-1]
    match = _REF_PATTERN.match(ref)
    if match:
        return context.ids[match.group(1)]
    if ref.isdigit():
        return int(ref)
    return _NONEXISTENT_ID_SENTINEL


def _read_cash_positions(context):
    conn = sqlite3.connect(context.cash_position_db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM cash_position").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@given("系統中有以下記帳交易（stock_analyzer 建立）：")
def step_given_stock_sync_transactions(context):
    repo = TransactionRepository(context.db_session)
    for row in context.table:
        account = context.accounts_by_name[row["account"]]
        transaction = repo.create(
            date=date.today(),
            amount=Decimal(row["amount"]),
            category_id=None,
            account_id=account.id,
            type=TransactionType(row["type"]),
            is_transfer=True,
            is_stock_sync=row["isStockSync"].strip().lower() == "true",
            currency="TWD",
        )
        context.ids[row["id"]] = transaction.id
    context.db_session.commit()


@when("stock_analyzer 推送以下現金異動：")
def step_when_create_stock_sync(context):
    row = context.table[0]
    payload = {}
    headings = context.table.headings
    if "direction" in headings and row["direction"]:
        payload["direction"] = row["direction"]
    if "amount" in headings and row["amount"] != "":
        payload["amount"] = float(row["amount"])
    if "currency" in headings and row["currency"]:
        payload["currency"] = row["currency"]
    if "accountName" in headings and row["accountName"]:
        payload["accountName"] = row["accountName"]
    context.last_response = context.api_client.post(
        "/api/stock-sync/transactions", json=payload
    )
    body = context.last_response.json()
    if body.get("success"):
        context.ids["__last_created__"] = body["data"]["id"]


@when('stock_analyzer 推送更新現金異動 "{ref}"：')
def step_when_update_stock_sync(context, ref):
    transaction_id = _resolve_ref(context, ref)
    row = context.table[0]
    payload = {"amount": float(row["amount"]), "direction": row["direction"]}
    context.last_response = context.api_client.put(
        f"/api/stock-sync/transactions/{transaction_id}", json=payload
    )


@when('stock_analyzer 推送刪除現金異動 "{ref}"')
def step_when_delete_stock_sync(context, ref):
    transaction_id = _resolve_ref(context, ref)
    context.last_response = context.api_client.delete(
        f"/api/stock-sync/transactions/{transaction_id}"
    )


@then("新建立的記帳交易應符合：")
def step_then_created_matches(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    assert (
        isinstance(data.get("id"), int) and data["id"] > 0
    ), f"Expected a valid id, got {data.get('id')}"
    expected = context.table[0]
    for heading in context.table.headings:
        expected_value = expected[heading].strip()
        if heading == "categoryId":
            assert (
                data.get("categoryId") is None
            ), f"categoryId: expected null, got {data.get('categoryId')}"
        elif heading == "amount":
            assert float(data.get("amount")) == float(
                expected_value
            ), f"amount: expected {expected_value}, got {data.get('amount')}"
        elif heading in ("isStockSync", "isTransfer"):
            assert (
                str(data.get(heading)).lower() == expected_value
            ), f"{heading}: expected {expected_value}, got {data.get(heading)}"
        else:
            assert (
                str(data.get(heading)) == expected_value
            ), f"{heading}: expected {expected_value}, got {data.get(heading)}"


@then('記帳交易 "{ref}" 應符合：')
def step_then_transaction_matches(context, ref):
    transaction_id = _resolve_ref(context, ref)
    context.db_session.expire_all()
    transaction = context.db_session.get(LedgerTransaction, transaction_id)
    expected = context.table[0]
    for heading in context.table.headings:
        expected_value = expected[heading].strip()
        actual_value = getattr(transaction, "type" if heading == "type" else heading)
        actual_value = (
            actual_value.value if hasattr(actual_value, "value") else actual_value
        )
        if heading == "amount":
            assert float(actual_value) == float(
                expected_value
            ), f"amount: expected {expected_value}, got {actual_value}"
        else:
            assert (
                str(actual_value) == expected_value
            ), f"{heading}: expected {expected_value}, got {actual_value}"


@then("不應觸發 CashPosition 同步")
def step_then_no_cash_position_sync(context):
    rows = _read_cash_positions(context)
    assert rows == [], f"Expected no CashPosition rows, got {rows}"
