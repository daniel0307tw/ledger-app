import os
import sqlite3
import tempfile
from types import SimpleNamespace

import httpx
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.core.deps import set_session_factory
from app.core.seed_data import DEFAULT_CATEGORIES
from app.main import create_app
from app.models import Base
from app.repositories.cash_position_repository import set_cash_position_db_path
from app.repositories.category_repository import CategoryRepository
from app.repositories.holding_repository import set_holding_http_transport


def _default_holdings_transport() -> httpx.MockTransport:
    """未在 scenario 中明確 Given 股票持倉資料時的預設值：兩個市場皆無持股。
    確保每個 scenario 起始狀態一致、絕不會意外打到真實的 stock_analyzer API。"""

    def handler(request: httpx.Request) -> httpx.Response:
        market = request.url.params.get("market", "tw")
        currency = "TWD" if market == "tw" else "USD"
        return httpx.Response(
            200, json={"market": market, "currency": currency, "portfolioMarketValue": 0, "holdings": []}
        )

    return httpx.MockTransport(handler)

postgres_container = None
engine = None
SessionLocal = None


def _create_cash_position_test_db() -> str:
    """建立一個隔離的暫存 SQLite 檔案，schema 比照 stock_analyzer 的 cash_position 表。
    測試絕不可碰真實的 stock_analyzer.db。
    """
    fd, path = tempfile.mkstemp(suffix=".db", prefix="cash_position_test_")
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE cash_position (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution VARCHAR NOT NULL,
            type VARCHAR NOT NULL DEFAULT 'Deposit',
            amount NUMERIC(14, 4) NOT NULL,
            currency VARCHAR NOT NULL,
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        )
        """
    )
    conn.commit()
    conn.close()
    return path


def before_all(context):
    global postgres_container, engine, SessionLocal

    postgres_container = PostgresContainer("postgres:15")
    postgres_container.start()

    db_url = postgres_container.get_connection_url().replace(
        "psycopg2", "psycopg"
    )
    os.environ["DATABASE_URL"] = db_url

    engine = create_engine(db_url)

    # Run Alembic migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")

    SessionLocal = sessionmaker(bind=engine)
    set_session_factory(SessionLocal)


def before_scenario(context, scenario):
    context.last_error = None
    context.last_response = None
    context.query_result = None
    context.ids = {}
    context.memo = {}
    context.accounts_by_name = {}

    context.db_session = SessionLocal()

    # 比照真實環境的 migration seed：每個 scenario 開始前重新建立 17 個預設分類
    # （after_scenario 會 TRUNCATE 所有資料表，包含 category，故每個 scenario 都要重新播種）。
    category_repo = CategoryRepository(context.db_session)
    context.categories_by_name = {
        name: category_repo.create(name=name, type=category_type) for name, category_type in DEFAULT_CATEGORIES
    }
    context.db_session.commit()

    app = create_app()
    from starlette.testclient import TestClient

    context.api_client = TestClient(app)
    context.repos = SimpleNamespace()
    context.services = SimpleNamespace()

    context.cash_position_db_path = _create_cash_position_test_db()
    set_cash_position_db_path(context.cash_position_db_path)

    set_holding_http_transport(_default_holdings_transport())


def after_scenario(context, scenario):
    if hasattr(context, "db_session") and context.db_session:
        context.db_session.rollback()
        # Truncate all tables except alembic_version
        for table in reversed(Base.metadata.sorted_tables):
            context.db_session.execute(
                text(f"TRUNCATE TABLE {table.name} CASCADE")
            )
        context.db_session.commit()
        context.db_session.close()

    if hasattr(context, "cash_position_db_path") and context.cash_position_db_path:
        try:
            os.remove(context.cash_position_db_path)
        except OSError:
            pass

    set_holding_http_transport(None)

    context.last_error = None
    context.last_response = None
    context.query_result = None
    context.ids = {}
    context.memo = {}
    context.accounts_by_name = {}


def after_all(context):
    global engine, postgres_container
    if engine:
        engine.dispose()
    if postgres_container:
        postgres_container.stop()
