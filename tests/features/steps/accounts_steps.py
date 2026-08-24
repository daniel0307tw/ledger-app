from behave import when


@when("使用者建立帳戶：")
def step_when_create_account(context):
    row = context.table[0]
    payload = {}
    if row["name"]:
        payload["name"] = row["name"]
    if row["type"]:
        payload["type"] = row["type"]
    context.last_response = context.api_client.post("/api/accounts", json=payload)


@when("使用者查詢帳戶列表")
def step_when_list_accounts(context):
    context.last_response = context.api_client.get("/api/accounts")
