from datetime import date
from decimal import Decimal

from behave import given, then, when

from app.repositories.budget_repository import BudgetRepository
from app.repositories.transaction_repository import TransactionRepository
from app.models.ledger_transaction import AdvancePaymentStatus, TransactionType


@given("系統中有以下預算：")
def step_given_budgets(context):
    repo = BudgetRepository(context.db_session)
    for row in context.table:
        category_id = None
        if row.get("category"):
            category_id = context.categories_by_name[row["category"]].id
        budget = repo.create(scope=row["scope"], category_id=category_id, monthly_amount=Decimal(row["monthly_amount"]))
        context.ids[row["id"]] = budget.id
    context.db_session.commit()


@given("系統中有以下收支紀錄（本月內）：")
def step_given_transactions_this_month(context):
    repo = TransactionRepository(context.db_session)
    has_transfer_column = "is_transfer" in context.table.headings
    has_advance_payment_column = "advancePaymentAmount" in context.table.headings
    has_advance_payment_status_column = "advancePaymentStatus" in context.table.headings
    for row in context.table:
        target_date = date.today() if row["date"] == "(本月)" else date.fromisoformat(row["date"])
        account = context.accounts_by_name[row["account"]]
        category = context.categories_by_name[row["category"]]
        is_transfer = row["is_transfer"].lower() == "true" if has_transfer_column else False
        advance_payment_amount = None
        if has_advance_payment_column and row["advancePaymentAmount"].strip():
            advance_payment_amount = Decimal(row["advancePaymentAmount"].strip())
        advance_payment_status = None
        if has_advance_payment_status_column and row["advancePaymentStatus"].strip():
            advance_payment_status = AdvancePaymentStatus(row["advancePaymentStatus"].strip())
        repo.create(
            date=target_date,
            amount=Decimal(row["amount"]),
            category_id=category.id,
            account_id=account.id,
            type=TransactionType(row["type"]),
            is_transfer=is_transfer,
            advance_payment_amount=advance_payment_amount,
            advance_payment_status=advance_payment_status,
        )
    context.db_session.commit()


@given("系統中無本月收支紀錄")
def step_given_no_transactions_this_month(context):
    pass


@when("使用者建立預算：")
def step_when_create_budget(context):
    row = context.table[0]
    payload = {"scope": row["scope"], "monthlyAmount": float(row["monthly_amount"])}
    if row.get("category"):
        payload["categoryId"] = context.categories_by_name[row["category"]].id
    context.last_response = context.api_client.post("/api/budgets", json=payload)
    body = context.last_response.json()
    if body.get("success"):
        context.ids["__last_created__"] = body["data"]["id"]


@when("使用者編輯預算 {budget_id}：")
def step_when_edit_budget(context, budget_id):
    resolved_id = context.ids.get(budget_id, int(budget_id) if budget_id.isdigit() else 999999999)
    row = context.table[0]
    payload = {"monthlyAmount": float(row["monthly_amount"])}
    context.last_response = context.api_client.put(f"/api/budgets/{resolved_id}", json=payload)


@when("使用者刪除預算 {budget_id}")
def step_when_delete_budget(context, budget_id):
    resolved_id = context.ids.get(budget_id, int(budget_id) if budget_id.isdigit() else 999999999)
    context.last_response = context.api_client.delete(f"/api/budgets/{resolved_id}")


@when("使用者查詢預算列表")
def step_when_list_budgets(context):
    context.last_response = context.api_client.get("/api/budgets")


@when("使用者查詢預算執行狀況")
def step_when_query_budget_status(context):
    context.last_response = context.api_client.get("/api/budgets/status")


@then("操作成功，預算符合：")
def step_then_budget_matches(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    expected = context.table[0]
    data = resp["data"]
    for heading in context.table.headings:
        if heading == "category":
            assert data["categoryId"] == context.categories_by_name[expected[heading]].id
        elif heading == "monthly_amount":
            assert float(data["monthlyAmount"]) == float(expected[heading])
        else:
            assert str(data.get(heading)) == expected[heading]


@then("操作成功，查詢結果應包含以下預算：")
def step_then_budget_list(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]

    def _category_id_or_none(value):
        return context.categories_by_name[value].id if value else None

    actual = {(item["scope"], item["categoryId"], float(item["monthlyAmount"])) for item in data}
    expected = {
        (row["scope"], _category_id_or_none(row.get("category")), float(row["monthly_amount"]))
        for row in context.table
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


@then("操作成功，執行狀況應包含：")
def step_then_budget_status(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    for row in context.table:
        category_id = context.categories_by_name[row["category"]].id
        match = next((item for item in data if item["categoryId"] == category_id), None)
        assert match is not None, f"No budget status found for category {row['category']}"
        assert float(match["monthlyAmount"]) == float(row["monthly_amount"])
        assert float(match["spent"]) == float(row["spent"])
        assert float(match["remaining"]) == float(row["remaining"])
        assert match["isOverBudget"] == (row["is_over_budget"].lower() == "true")
