from datetime import date
from decimal import Decimal

from behave import given, then, when

from app.models.ledger_transaction import LedgerTransaction
from app.repositories.recurring_transaction_repository import RecurringTransactionRepository
from app.repositories.transaction_repository import TransactionRepository


@given("系統中有以下固定收支規則：")
def step_given_recurring_transactions(context):
    repo = RecurringTransactionRepository(context.db_session)
    for row in context.table:
        account = context.accounts_by_name[row["account"]]
        category = context.categories_by_name[row["category"]]
        rule = repo.create(
            frequency=row["frequency"],
            amount=Decimal(row["amount"]),
            category_id=category.id,
            account_id=account.id,
            type=row["type"],
            start_date=date.fromisoformat(row["start_date"]),
            generate_count=int(row["generate_count"]),
            status=row["status"] if "status" in context.table.headings else "啟用",
        )
        context.ids[row["id"]] = rule.id
    context.db_session.commit()


@given("規則 {rule_id} 已生成以下交易：")
def step_given_generated_transactions(context, rule_id):
    resolved_id = context.ids[rule_id]
    repo = TransactionRepository(context.db_session)
    rule_repo = RecurringTransactionRepository(context.db_session)
    rule = rule_repo.find(resolved_id)
    for row in context.table:
        repo.create(
            date=date.fromisoformat(row["date"]),
            amount=Decimal(row["amount"]),
            category_id=rule.category_id,
            account_id=rule.account_id,
            type=rule.type,
            source_recurring_transaction_id=resolved_id,
        )
    context.db_session.commit()


@when("使用者建立固定收支規則：")
def step_when_create_recurring_transaction(context):
    row = context.table[0]
    payload = {
        "frequency": row["frequency"],
        "amount": float(row["amount"]),
        "categoryId": context.categories_by_name[row["category"]].id,
        "accountId": context.accounts_by_name[row["account"]].id,
        "type": row["type"],
        "startDate": row["start_date"],
        "generateCount": int(row["generate_count"]),
    }
    context.last_response = context.api_client.post("/api/recurring-transactions", json=payload)
    body = context.last_response.json()
    if body.get("success"):
        context.ids["__last_created__"] = body["data"]["id"]


@when("使用者編輯固定收支規則 {rule_id}：")
def step_when_edit_recurring_transaction(context, rule_id):
    resolved_id = context.ids.get(rule_id, 999999999 if not rule_id.isdigit() else int(rule_id))
    row = context.table[0]
    payload = {
        "frequency": row["frequency"],
        "amount": float(row["amount"]),
        "categoryId": context.categories_by_name[row["category"]].id,
        "accountId": context.accounts_by_name[row["account"]].id,
        "type": row["type"],
        "startDate": row["start_date"],
        "generateCount": int(row["generate_count"]),
    }
    context.last_response = context.api_client.put(f"/api/recurring-transactions/{resolved_id}", json=payload)


@when("使用者刪除固定收支規則 {rule_id}")
def step_when_delete_recurring_transaction(context, rule_id):
    resolved_id = context.ids.get(rule_id, 999999999 if not rule_id.isdigit() else int(rule_id))
    context.last_response = context.api_client.delete(f"/api/recurring-transactions/{resolved_id}")


@when("使用者查詢固定收支規則列表")
def step_when_list_recurring_transactions(context):
    context.last_response = context.api_client.get("/api/recurring-transactions")


@when("使用者對規則 {rule_id} 補生成固定收支交易")
def step_when_generate_recurring_transaction(context, rule_id):
    resolved_id = context.ids[rule_id]
    context.last_response = context.api_client.post(f"/api/recurring-transactions/{resolved_id}/generate")


@then("操作成功，規則符合：")
def step_then_rule_matches(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    expected = context.table[0]
    data = resp["data"]
    for heading in context.table.headings:
        if heading == "category":
            assert data["categoryId"] == context.categories_by_name[expected[heading]].id
        elif heading == "account":
            assert data["accountId"] == context.accounts_by_name[expected[heading]].id
        elif heading == "amount":
            assert float(data["amount"]) == float(expected[heading])
        elif heading == "generate_count":
            assert data["generateCount"] == int(expected[heading])
        else:
            assert str(data.get(heading)) == expected[heading], f"{heading}: expected {expected[heading]}, got {data.get(heading)}"


@then("操作成功，應生成以下 {n} 筆交易：")
def step_then_generated_transactions(context, n):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    rule_id = resp["data"]["id"]
    context.db_session.expire_all()
    transactions = TransactionRepository(context.db_session).find_by_source_recurring_transaction(rule_id)
    assert len(transactions) == int(n), f"Expected {n} transactions, got {len(transactions)}"
    actual = {(t.date.isoformat(), float(t.amount)) for t in transactions}
    expected = {(row["date"], float(row["amount"])) for row in context.table}
    assert actual == expected, f"Expected {expected}, got {actual}"


@then("操作成功，已生成的交易金額應不受影響：")
def step_then_generated_transaction_amounts_unchanged(context):
    for row in context.table:
        target_date = date.fromisoformat(row["date"])
        transaction = (
            context.db_session.query(LedgerTransaction)
            .filter(LedgerTransaction.date == target_date)
            .order_by(LedgerTransaction.id.desc())
            .first()
        )
        assert transaction is not None, f"No transaction found for date {row['date']}"
        assert float(transaction.amount) == float(row["amount"])


@then("操作成功，規則已刪除但以下交易應仍存在：")
def step_then_transactions_still_exist_after_delete(context):
    for row in context.table:
        target_date = date.fromisoformat(row["date"])
        transaction = (
            context.db_session.query(LedgerTransaction)
            .filter(LedgerTransaction.date == target_date, LedgerTransaction.amount == Decimal(row["amount"]))
            .first()
        )
        assert transaction is not None, f"Expected transaction on {row['date']} amount {row['amount']} to still exist"


@then("操作成功，查詢結果應包含以下固定收支規則：")
def step_then_recurring_transaction_list(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    actual = {(item["frequency"], float(item["amount"]), item["status"]) for item in data}
    expected = {(row["frequency"], float(row["amount"]), row["status"]) for row in context.table}
    assert actual == expected, f"Expected {expected}, got {actual}"


@then("操作成功，本次應補生成 {n} 筆交易：")
@then("操作成功，本次應補生成 {n} 筆交易")
def step_then_generated_count(context, n):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    assert resp["data"]["generatedCount"] == int(n), (
        f"Expected generatedCount={n}, got {resp['data']['generatedCount']}"
    )
    if int(n) > 0 and context.table is not None:
        actual = {(t["date"], float(t["amount"])) for t in resp["data"]["transactions"]}
        expected = {(row["date"], float(row["amount"])) for row in context.table}
        assert actual == expected, f"Expected {expected}, got {actual}"
