import httpx
from behave import given, then, when

from app.repositories.holding_repository import set_holding_http_transport

MARKET_BY_CURRENCY = {"TWD": "tw", "USD": "us"}
CURRENCY_BY_MARKET = {"tw": "TWD", "us": "USD"}


@given("stock_analyzer 有以下股票持倉：")
def step_given_stock_holdings(context):
    rows_by_market: dict[str, list[dict]] = {"tw": [], "us": []}
    for row in context.table:
        market = MARKET_BY_CURRENCY[row["currency"]]
        rows_by_market[market].append(
            {
                "symbol": row["symbol"],
                "name": row["name"],
                "marketValue": float(row["market_value"]),
                "unrealizedPnl": float(row["unrealized_pnl"]),
            }
        )

    context.stock_analyzer_requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        # 記錄呼叫端點（method + path），供「刷新資產總覽」驗證確實打到 refresh 端點、
        # 不是查詢端點；不影響既有查詢情境的斷言，純附加記錄。
        context.stock_analyzer_requests.append((request.method, request.url.path))
        market = request.url.params["market"]
        holdings = rows_by_market.get(market, [])
        return httpx.Response(
            200,
            json={
                "market": market,
                "currency": CURRENCY_BY_MARKET[market],
                "portfolioMarketValue": sum(h["marketValue"] for h in holdings),
                "holdings": holdings,
            },
        )

    set_holding_http_transport(httpx.MockTransport(handler))


@given("stock_analyzer 尚無任何股票持倉")
def step_given_no_holdings(context):
    def handler(request: httpx.Request) -> httpx.Response:
        market = request.url.params["market"]
        return httpx.Response(
            200,
            json={"market": market, "currency": CURRENCY_BY_MARKET[market], "portfolioMarketValue": 0, "holdings": []},
        )

    set_holding_http_transport(httpx.MockTransport(handler))


@given("stock_analyzer 的股票資料查詢服務暫時無法連線")
def step_given_stock_service_unavailable(context):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    set_holding_http_transport(httpx.MockTransport(handler))


@when("使用者查詢資產總覽")
def step_when_query_net_worth(context):
    context.last_response = context.api_client.get("/api/net-worth")


@when("使用者刷新資產總覽")
def step_when_refresh_net_worth(context):
    context.last_response = context.api_client.post("/api/net-worth/refresh")


@then("操作成功，查詢結果應包含以下現金與信用卡總額：")
def step_then_cash_credit_total(context):
    assert context.last_response.status_code == 200, context.last_response.text
    body = context.last_response.json()
    assert body["success"] is True, body
    row = context.table[0]
    data = body["data"]
    assert data["cashTotal"] == float(row["cash_total"]), data
    assert data["creditCardDebtTotal"] == float(row["credit_card_debt_total"]), data


@then("查詢結果應包含以下股票個股明細：")
def step_then_stock_holdings(context):
    data = context.last_response.json()["data"]
    expected = {
        (row["currency"], row["symbol"], row["name"], float(row["market_value"]), float(row["unrealized_pnl"]))
        for row in context.table
    }
    actual = {
        (h["currency"], h["symbol"], h["name"], h["marketValue"], h["unrealizedPnl"]) for h in data["stockHoldings"]
    }
    assert expected == actual, (expected, actual)


@then("操作成功，查詢結果應包含以下幣別資產小計：")
@then("查詢結果應包含以下幣別資產小計：")
def step_then_currency_totals(context):
    data = context.last_response.json()["data"]
    expected = {(row["currency"], float(row["total"])) for row in context.table}
    actual = {(c["currency"], c["total"]) for c in data["currencyTotals"]}
    assert expected == actual, (expected, actual)


@then("查詢結果中的股票資料應標示查詢失敗")
def step_then_stock_data_failed(context):
    data = context.last_response.json()["data"]
    assert data["stockDataStatus"] == "failed", data


@then("查詢結果應顯示尚無持股")
def step_then_no_holdings_display(context):
    data = context.last_response.json()["data"]
    assert data["stockHoldings"] == [], data
    assert data["stockDataStatus"] == "ok", data


@then("操作應呼叫股票資料來源的刷新端點")
def step_then_called_refresh_endpoint(context):
    requests = getattr(context, "stock_analyzer_requests", [])
    assert requests, "沒有任何呼叫紀錄，Given 步驟可能沒有正確設定 mock transport"
    for method, path in requests:
        assert method == "POST", f"預期呼叫刷新端點應為 POST，實際為 {method} {path}"
        assert path == "/api/portfolio/refresh", f"預期呼叫 /api/portfolio/refresh，實際為 {method} {path}"
