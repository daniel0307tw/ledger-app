from datetime import date
from decimal import Decimal

from behave import given, then, when

from app.models.cloud_invoice import CloudInvoice, CloudInvoiceStatus
from app.repositories.cloud_invoice_repository import CloudInvoiceRepository

_RESULT_LABEL_TO_CODE = {
    "已建立": "created",
    "待確認": "pending_review",
    "已略過": "skipped",
    "資料錯誤": "invalid",
}


@given("系統中無其他既有雲端發票紀錄")
def step_given_no_cloud_invoices(context):
    pass


@given("系統中無其他既有雲端發票紀錄與收支紀錄")
def step_given_no_cloud_invoices_and_transactions(context):
    pass


@given("系統中無任何雲端發票同步紀錄")
def step_given_no_cloud_invoice_sync_records(context):
    pass


@given("系統中有以下雲端發票同步紀錄：")
def step_given_cloud_invoices(context):
    repo = CloudInvoiceRepository(context.db_session)
    has_status_column = "status" in context.table.headings
    for row in context.table:
        status = CloudInvoiceStatus(row["status"]) if has_status_column else CloudInvoiceStatus.PENDING_REVIEW
        invoice = repo.create(
            invoice_number=row["invoice_number"],
            invoice_date=date.fromisoformat(row["invoice_date"]),
            amount=Decimal(row["amount"]),
            seller_name=row["seller_name"],
            status=status,
        )
        context.memo[f"cloud_invoice_{row['invoice_number']}"] = invoice.id
    context.db_session.commit()


@when("Hermes 傳送以下雲端發票資料進行同步：")
def step_when_sync_cloud_invoices(context):
    payload = []
    has_item_summary_column = "item_summary" in context.table.headings
    has_suggested_category_column = "建議分類" in context.table.headings
    for row in context.table:
        item = {
            "invoiceNumber": row["invoice_number"],
            "invoiceDate": row["invoice_date"],
            "sellerName": row["seller_name"],
        }
        if row.get("amount"):
            item["amount"] = float(row["amount"])
        if has_item_summary_column and row["item_summary"].strip():
            item["itemSummary"] = row["item_summary"].strip()
        if has_suggested_category_column and row["建議分類"].strip():
            item["categoryId"] = context.categories_by_name[row["建議分類"].strip()].id
        payload.append(item)
    context.last_response = context.api_client.post("/api/cloud-invoices/sync", json=payload)


@then("操作成功，同步結果應包含以下逐筆處理：")
def step_then_sync_results(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    actual = {row["invoiceNumber"]: row["result"] for row in data}
    expected = {row["invoice_number"]: _RESULT_LABEL_TO_CODE[row["結果"]] for row in context.table}
    assert actual == expected, f"Expected {expected}, got {actual}"


@when("使用者查詢待確認雲端發票清單")
def step_when_list_pending_cloud_invoices(context):
    context.last_response = context.api_client.get("/api/cloud-invoices/pending")


@then("操作成功，查詢結果應包含以下待確認發票：")
def step_then_pending_cloud_invoices(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    actual = {
        (row["invoiceNumber"], row["invoiceDate"], float(row["amount"]), row["sellerName"]) for row in data
    }
    expected = {
        (row["invoice_number"], row["invoice_date"], float(row["amount"]), row["seller_name"])
        for row in context.table
    }
    assert actual == expected, f"Expected {expected}, got {actual}"


@when('使用者將編號 {invoice_number} 的待確認發票標記為"{decision_label}"')
def step_when_confirm_cloud_invoice(context, invoice_number, decision_label):
    decision = "confirm_new" if decision_label == "確認為新交易" else "confirm_duplicate"
    invoice_id = context.memo[f"cloud_invoice_{invoice_number}"]
    context.last_response = context.api_client.post(
        f"/api/cloud-invoices/{invoice_id}/confirm", json={"decision": decision}
    )


@then('操作成功，該筆發票狀態應變為"{status}"')
def step_then_cloud_invoice_status(context, status):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    assert resp["data"]["status"] == status, f"Expected status={status}, got {resp['data']['status']}"


@then('操作成功，應建立一筆支出交易，帳戶為"{account_name}"、分類為"{category_name}"、金額為 {amount}')
def step_then_expense_transaction_created(context, account_name, category_name, amount):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    # 批次同步的回應是逐筆結果陣列；確認待確認發票的回應是單一物件。兩種呼叫端都可能用到這個 Then。
    transaction_id = data[0]["transactionId"] if isinstance(data, list) else data.get("transactionId")
    context.db_session.expire_all()
    from app.models.ledger_transaction import LedgerTransaction

    transaction = context.db_session.get(LedgerTransaction, transaction_id)
    assert transaction is not None, f"Transaction {transaction_id} not found"
    assert float(transaction.amount) == float(amount)
    assert context.accounts_by_name[account_name].id == transaction.account_id
    assert context.categories_by_name[category_name].id == transaction.category_id


@when("使用者查詢雲端發票同步健康狀態")
def step_when_query_health(context):
    context.last_response = context.api_client.get("/api/cloud-invoices/health")


@then("操作成功，健康狀態應包含：")
def step_then_health_contains(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    row = context.table[0]
    if "pending_count" in context.table.headings:
        assert data["pendingCount"] == int(row["pending_count"])
    if "synced_count" in context.table.headings:
        assert data["syncedCount"] == int(row["synced_count"])


@then("操作成功，應顯示尚無同步紀錄")
def step_then_no_sync_history(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    assert resp["data"]["hasSyncHistory"] is False, f"Expected hasSyncHistory=false, got {resp['data']}"
