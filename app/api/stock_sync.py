from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.stock_sync import (
    StockSyncTransactionInput,
    StockSyncTransactionOut,
    StockSyncTransactionUpdateInput,
)
from app.services.stock_sync_service import StockSyncService

router = APIRouter()


@router.post("/stock-sync/transactions", status_code=201)
def create_stock_sync_transaction(
    payload: StockSyncTransactionInput, db: Session = Depends(get_db)
):
    service = StockSyncService(db)
    transaction = service.create_stock_sync_transaction(
        direction=payload.direction,
        amount=payload.amount,
        currency=payload.currency,
        account_name=payload.account_name,
    )
    return {
        "success": True,
        "data": StockSyncTransactionOut.model_validate(transaction).model_dump(
            by_alias=True
        ),
    }


@router.put("/stock-sync/transactions/{id}")
def update_stock_sync_transaction(
    id: int, payload: StockSyncTransactionUpdateInput, db: Session = Depends(get_db)
):
    service = StockSyncService(db)
    transaction = service.update_stock_sync_transaction(
        id, amount=payload.amount, direction=payload.direction
    )
    return {
        "success": True,
        "data": StockSyncTransactionOut.model_validate(transaction).model_dump(
            by_alias=True
        ),
    }


@router.delete("/stock-sync/transactions/{id}")
def delete_stock_sync_transaction(id: int, db: Session = Depends(get_db)):
    service = StockSyncService(db)
    service.delete_stock_sync_transaction(id)
    return {"success": True}
