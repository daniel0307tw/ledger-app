from sqlalchemy.orm import Session

from app.models.account import AccountType
from app.repositories.holding_repository import HoldingFetchError, HoldingRepository
from app.services.account_service import AccountService

MARKET_CURRENCY = {"tw": "TWD", "us": "USD"}


class NetWorthService:
    """彙整現金/信用卡（本地 account）+ 股票市值（stock_analyzer 唯讀 API）為資產總覽。

    account 表無 currency 欄位，現金/信用卡負債恆為 TWD；USD 小計僅由美股市值構成，
    不做任何匯率換算（見 specs/features/系統抽象.md 變異點索引）。
    """

    def __init__(self, session: Session):
        self.account_service = AccountService(session)
        self.holdings = HoldingRepository()

    def get_net_worth(self) -> dict:
        return self._build_net_worth(self.holdings.get_holdings)

    def refresh_net_worth(self) -> dict:
        """比照 get_net_worth，但股票市值改用 refresh_holdings——會真的觸發
        stock_analyzer 去外部 API 抓即時市價、落地保存快照，不是讀既有快照。
        只給使用者主動要求更新時呼叫（例如資產頁下拉刷新），見
        HoldingRepository.refresh_holdings 的完整說明"""
        return self._build_net_worth(self.holdings.refresh_holdings)

    def _build_net_worth(self, fetch_market_holdings) -> dict:
        accounts = self.account_service.list_accounts()
        cash_total = sum(a["balance"] for a in accounts if a["type"] == AccountType.GENERAL)
        credit_card_debt_total = sum(a["balance"] for a in accounts if a["type"] == AccountType.CREDIT_CARD)

        stock_holdings: list[dict] = []
        stock_value_by_currency: dict[str, float] = {}
        stock_data_status = "ok"

        for market, currency in MARKET_CURRENCY.items():
            try:
                data = fetch_market_holdings(market)
            except HoldingFetchError:
                stock_data_status = "failed"
                continue
            stock_value_by_currency[currency] = data["portfolioMarketValue"]
            for holding in data["holdings"]:
                stock_holdings.append(
                    {
                        "currency": currency,
                        "symbol": holding["symbol"],
                        "name": holding["name"],
                        "marketValue": holding["marketValue"],
                        "unrealizedPnl": holding["unrealizedPnl"],
                    }
                )

        twd_stock_value = stock_value_by_currency.get("TWD", 0.0) if stock_data_status == "ok" else 0.0
        usd_stock_value = stock_value_by_currency.get("USD", 0.0) if stock_data_status == "ok" else 0.0
        currency_candidates = {
            "TWD": cash_total + credit_card_debt_total + twd_stock_value,
            "USD": usd_stock_value,
        }
        # 完全無資產的幣別不列入（比照 stock_analyzer 既有的總資產顯示慣例）；
        # 用 != 0（而非 > 0）以確保純負債（例如只有信用卡欠款）仍會顯示，不被誤判為「無資產」。
        currency_totals = [
            {"currency": currency, "total": total}
            for currency, total in sorted(currency_candidates.items())
            if total != 0
        ]

        return {
            "cashTotal": cash_total,
            "creditCardDebtTotal": credit_card_debt_total,
            "stockHoldings": stock_holdings,
            "currencyTotals": currency_totals,
            "stockDataStatus": stock_data_status,
        }
