import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/ledger_app_dev",
    )
    API_PREFIX: str = "/api"

    # 股票分析系統 (stock_analyzer) 的 CashPosition 資料表所在的 SQLite 檔案。
    # 這是外部系統實際在用的那份資料庫，本專案只讀寫這張表，不 import 對方程式碼、不改對方 schema。
    # 測試環境務必覆寫此路徑（見 tests/features/environment.py），絕不可讓測試碰到真實資料。
    CASH_POSITION_DB_PATH: str = os.getenv(
        "CASH_POSITION_DB_PATH",
        "/home/daniel/stock_analyzer/data/stock_analyzer.db",
    )

    # stock_analyzer 提供的唯讀股票持倉 API（見 app/repositories/holding_repository.py）。
    # 測試環境務必透過 set_holding_http_transport() 覆寫 HTTP transport，絕不可讓測試打到這個真實服務。
    STOCK_ANALYZER_API_BASE_URL: str = os.getenv(
        "STOCK_ANALYZER_API_BASE_URL",
        "http://127.0.0.1:8100",
    )


settings = Settings()
