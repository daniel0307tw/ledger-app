from fastapi import APIRouter

from app.api.accounts import router as accounts_router
from app.api.budgets import router as budgets_router
from app.api.categories import router as categories_router
from app.api.cloud_invoices import router as cloud_invoices_router
from app.api.net_worth import router as net_worth_router
from app.api.recurring_transactions import router as recurring_transactions_router
from app.api.reports import router as reports_router
from app.api.stock_sync import router as stock_sync_router
from app.api.transactions import router as transactions_router
from app.api.transfers import router as transfers_router

router = APIRouter()
router.include_router(accounts_router)
router.include_router(categories_router)
router.include_router(net_worth_router)
router.include_router(reports_router)
router.include_router(transactions_router)
router.include_router(transfers_router)
router.include_router(cloud_invoices_router)
router.include_router(recurring_transactions_router)
router.include_router(budgets_router)
router.include_router(stock_sync_router)
