from behave import then, when

_NONEXISTENT_ID_SENTINEL = 999999999
_NONEXISTENT_ACCOUNT_NAME = "不存在的帳戶"


def _resolve_account_id(context, name: str):
    if name == _NONEXISTENT_ACCOUNT_NAME:
        return _NONEXISTENT_ID_SENTINEL
    return context.accounts_by_name[name].id


@when("使用者將帳戶轉帳：")
def step_when_transfer(context):
    row = context.table[0]
    payload = {
        "fromAccountId": _resolve_account_id(context, row["from_account"]),
        "toAccountId": _resolve_account_id(context, row["to_account"]),
        "amount": float(row["amount"]),
        "date": row["date"],
    }
    context.last_response = context.api_client.post("/api/transfers", json=payload)


@then("應建立一筆轉出紀錄與一筆轉入紀錄：")
def step_then_transfer_pair_created(context):
    resp = context.last_response.json()
    assert resp.get("success") is True, f"Expected success, got {resp}"
    data = resp["data"]
    assert len(data) == 2, f"Expected 2 transactions, got {len(data)}"

    for expected, actual in zip(context.table, data):
        expected_account_id = context.accounts_by_name[expected["account"]].id
        assert actual["accountId"] == expected_account_id
        assert actual["type"] == expected["type"]
        assert float(actual["amount"]) == float(expected["amount"])
        assert str(actual["isTransfer"]).lower() == expected["is_transfer"]

    group_ids = {row["transferGroupId"] for row in data}
    assert len(group_ids) == 1 and None not in group_ids, (
        f"Expected both legs to share the same transfer_group_id, got {group_ids}"
    )
