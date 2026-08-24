from __future__ import annotations

from sqlalchemy import Column, DateTime, Integer, MetaData, Numeric, String, Table, create_engine, delete, func, insert
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

_external_metadata = MetaData()

cash_position_table = Table(
    "cash_position",
    _external_metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("institution", String, nullable=False),
    Column("type", String, nullable=False, server_default="Deposit"),
    Column("amount", Numeric(14, 4), nullable=False),
    Column("currency", String, nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
)


class CashPositionSyncError(Exception):
    """寫入/刪除外部 stock_analyzer CashPosition 資料表失敗（例如 SQLite 檔案被鎖住）。"""


# settings.CASH_POSITION_DB_PATH 是模組載入當下就固定的類別屬性（os.getenv 只會呼叫一次），
# 之後再改環境變數不會反映到已經 import 過的 settings 物件——這與 app.core.deps 的
# _session_factory 是同一個問題、同一種解法：測試環境要覆寫連線目標時，透過這個
# module-level 變數明確覆寫，而不是依賴 settings 在 import 之後才變動。
_db_path_override: str | None = None


def set_cash_position_db_path(path: str) -> None:
    global _db_path_override
    _db_path_override = path


class CashPositionRepository:
    """讀寫外部系統 stock_analyzer 的 CashPosition 資料表（唯讀參考對方 schema，不 import 對方程式碼）。

    連線目標依序取：明確傳入的 db_path → set_cash_position_db_path() 覆寫值
    → settings.CASH_POSITION_DB_PATH（真實 stock_analyzer.db）。
    測試環境務必呼叫 set_cash_position_db_path() 指向隔離的暫存 SQLite 檔案，絕不可讓測試寫到真實資料。
    """

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or _db_path_override or settings.CASH_POSITION_DB_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}")

    def create(self, institution: str, amount, currency: str, type: str) -> int:
        try:
            with self.engine.begin() as conn:
                result = conn.execute(
                    insert(cash_position_table).values(
                        institution=institution, amount=amount, currency=currency, type=type
                    )
                )
                return result.inserted_primary_key[0]
        except SQLAlchemyError as exc:
            raise CashPositionSyncError(str(exc)) from exc

    def delete(self, cash_position_id: int) -> None:
        try:
            with self.engine.begin() as conn:
                conn.execute(delete(cash_position_table).where(cash_position_table.c.id == cash_position_id))
        except SQLAlchemyError as exc:
            raise CashPositionSyncError(str(exc)) from exc
