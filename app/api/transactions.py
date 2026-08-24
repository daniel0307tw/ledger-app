from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.transaction import SettleAdvancePaymentInput, TransactionInput, TransactionOut
from app.services.transaction_service import TransactionService

router = APIRouter()


@router.post("/transactions", status_code=201)
def create_transaction(payload: TransactionInput, db: Session = Depends(get_db)):
    service = TransactionService(db)
    transaction = service.create_transaction(
        date=payload.date,
        amount=payload.amount,
        category_id=payload.category_id,
        account_id=payload.account_id,
        type=payload.type,
        note=payload.note,
        advance_payment_amount=payload.advance_payment_amount,
    )
    return {"success": True, "data": TransactionOut.model_validate(transaction).model_dump(by_alias=True)}


# 固定路徑，須排在 "/transactions/{transaction_id}" 系列路由之前註冊；比照既有
# GET /cloud-invoices/pending 的慣例（雖然本檔目前沒有 GET /transactions/{id}，
# 這裡仍維持同樣的註冊順序慣例，避免未來新增 GET /transactions/{id} 時反而需要調動這裡）。
@router.get("/transactions/pending-advance-payments")
def list_pending_advance_payments(db: Session = Depends(get_db)):
    service = TransactionService(db)
    transactions = service.list_pending_advance_payments()
    return {
        "success": True,
        "data": [TransactionOut.model_validate(t).model_dump(by_alias=True) for t in transactions],
    }


@router.post("/transactions/{transaction_id}/settle-advance-payment")
def settle_advance_payment(transaction_id: int, payload: SettleAdvancePaymentInput, db: Session = Depends(get_db)):
    service = TransactionService(db)
    settlement_transaction, advance_payment_transaction = service.settle_advance_payment(
        transaction_id,
        date=payload.date,
        amount=payload.amount,
        account_id=payload.account_id,
    )
    return {
        "success": True,
        "data": {
            "settlementTransaction": TransactionOut.model_validate(settlement_transaction).model_dump(
                by_alias=True
            ),
            "advancePaymentTransaction": TransactionOut.model_validate(advance_payment_transaction).model_dump(
                by_alias=True
            ),
        },
    }


@router.put("/transactions/{transaction_id}")
def update_transaction(transaction_id: int, payload: TransactionInput, db: Session = Depends(get_db)):
    service = TransactionService(db)
    transaction = service.update_transaction(
        transaction_id,
        date=payload.date,
        amount=payload.amount,
        category_id=payload.category_id,
        account_id=payload.account_id,
        type=payload.type,
        note=payload.note,
        advance_payment_amount=payload.advance_payment_amount,
    )
    return {"success": True, "data": TransactionOut.model_validate(transaction).model_dump(by_alias=True)}


@router.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    service = TransactionService(db)
    service.delete_transaction(transaction_id)
    return {"success": True}


@router.get("/transactions")
def list_transactions(startDate: date, endDate: date, db: Session = Depends(get_db)):
    service = TransactionService(db)
    transactions = service.list_transactions(startDate, endDate)
    return {
        "success": True,
        "data": [TransactionOut.model_validate(t).model_dump(by_alias=True) for t in transactions],
    }
