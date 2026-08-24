from typing import Literal

from pydantic import BaseModel


class StockHoldingOut(BaseModel):
    currency: Literal["TWD", "USD"]
    symbol: str
    name: str
    marketValue: float
    unrealizedPnl: float


class CurrencyTotalOut(BaseModel):
    currency: Literal["TWD", "USD"]
    total: float


class NetWorthOut(BaseModel):
    cashTotal: float
    creditCardDebtTotal: float
    stockHoldings: list[StockHoldingOut]
    currencyTotals: list[CurrencyTotalOut]
    stockDataStatus: Literal["ok", "failed"]
