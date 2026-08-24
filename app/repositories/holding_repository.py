from __future__ import annotations

import httpx

from app.core.config import settings

# 測試環境務必呼叫 set_holding_http_transport() 覆寫為 httpx.MockTransport，絕不可讓測試
# 打到真實的 stock_analyzer API——與 CashPositionRepository 的 set_cash_position_db_path()
# 是同一種「module-level 覆寫值」解法，只是外部資源型態從 SQLite 檔案換成 HTTP 服務。
_transport_override: httpx.BaseTransport | None = None


def set_holding_http_transport(transport: httpx.BaseTransport | None) -> None:
    global _transport_override
    _transport_override = transport


class HoldingFetchError(Exception):
    """呼叫 stock_analyzer 唯讀股票持倉 API 失敗（連線逾時、服務不可用等）。"""


class HoldingRepository:
    """唯讀查詢外部系統 stock_analyzer 的股票持倉 API（不寫入、不 import 對方程式碼）。"""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.STOCK_ANALYZER_API_BASE_URL

    def get_holdings(self, market: str) -> dict:
        try:
            with httpx.Client(base_url=self.base_url, transport=_transport_override, timeout=3.0) as client:
                response = client.get("/api/portfolio/holdings", params={"market": market})
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise HoldingFetchError(str(exc)) from exc

    def refresh_holdings(self, market: str) -> dict:
        """觸發 stock_analyzer 真的去外部 API 抓即時市價並落地保存快照（會消耗
        FindMind/FMP 額度），不是唯讀查詢——只給使用者主動要求更新時呼叫（例如資產頁
        下拉刷新）。timeout 拉長到 10 秒，因為這條路徑真的要打外部股價 API，不像
        get_holdings 只是讀 stock_analyzer 自己的資料庫"""
        try:
            with httpx.Client(base_url=self.base_url, transport=_transport_override, timeout=10.0) as client:
                response = client.post("/api/portfolio/refresh", params={"market": market})
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            raise HoldingFetchError(str(exc)) from exc
