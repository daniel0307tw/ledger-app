from behave import then, use_step_matcher, when

use_step_matcher("re")


@when(r"使用者查詢分類花費統計，起始日期 (?P<start_date>.*?) 結束日期 (?P<end_date>.*)")
def step_when_query_category_summary(context, start_date, end_date):
    params = {}
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    context.last_response = context.api_client.get("/api/reports/category-summary", params=params)


@when(
    r"使用者查詢分類花費明細，分類 (?P<category>.*?) 起始日期 (?P<start_date>.*?) 結束日期 (?P<end_date>.*)"
)
def step_when_query_category_detail(context, category, start_date, end_date):
    params = {}
    if category:
        params["category"] = category
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date
    context.last_response = context.api_client.get("/api/reports/category-detail", params=params)


use_step_matcher("parse")


@then("操作成功，查詢結果應包含以下分類花費統計：")
def step_then_category_summary_contains(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    expected_rows = list(context.table)

    actual = {(row["category"], float(row["totalAmount"])) for row in data}
    expected = {(row["category"], float(row["total_amount"])) for row in expected_rows}
    assert actual == expected, f"Expected {expected}, got {actual}"


@then("操作成功，查詢結果應包含以下收支紀錄明細：")
def step_then_category_detail_contains(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    expected_rows = list(context.table)
    assert len(data) == len(expected_rows), f"Expected {len(expected_rows)} rows, got {len(data)}: {data}"

    headings = context.table.headings
    for expected, actual in zip(expected_rows, data):
        if "date" in headings:
            assert actual["date"] == expected["date"], f"date: expected {expected['date']}, got {actual['date']}"
        if "category" in headings:
            expected_category_id = context.categories_by_name[expected["category"]].id
            assert actual["categoryId"] == expected_category_id, (
                f"categoryId: expected {expected_category_id}, got {actual['categoryId']}"
            )
        if "amount" in headings:
            assert float(actual["amount"]) == float(expected["amount"]), (
                f"amount: expected {expected['amount']}, got {actual['amount']}"
            )
        if "account" in headings:
            expected_account_id = context.accounts_by_name[expected["account"]].id
            assert actual["accountId"] == expected_account_id, (
                f"accountId: expected {expected_account_id}, got {actual['accountId']}"
            )
        if "note" in headings:
            expected_note = expected["note"].strip() or None
            assert actual.get("note") == expected_note, f"note: expected {expected_note}, got {actual.get('note')}"
        if "advancePaymentAmount" in headings:
            expected_amount = (
                float(expected["advancePaymentAmount"]) if expected["advancePaymentAmount"].strip() else None
            )
            actual_amount = actual.get("advancePaymentAmount")
            actual_amount = float(actual_amount) if actual_amount is not None else None
            assert actual_amount == expected_amount, (
                f"advancePaymentAmount: expected {expected_amount}, got {actual_amount}"
            )
        if "advancePaymentStatus" in headings:
            expected_status = expected["advancePaymentStatus"].strip() or None
            assert actual.get("advancePaymentStatus") == expected_status, (
                f"advancePaymentStatus: expected {expected_status}, got {actual.get('advancePaymentStatus')}"
            )
