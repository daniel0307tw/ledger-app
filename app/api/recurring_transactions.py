from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.recurring_transaction import RecurringTransactionInput, RecurringTransactionOut
from app.schemas.transaction import TransactionOut
from app.services.recurring_transaction_service import RecurringTransactionService

router = APIRouter()


@router.post("/recurring-transactions", status_code=201)
def create_recurring_transaction(payload: RecurringTransactionInput, db: Session = Depends(get_db)):
    service = RecurringTransactionService(db)
    rule, _created = service.create_rule(
        frequency=payload.frequency,
        amount=payload.amount,
        category_id=payload.category_id,
        account_id=payload.account_id,
        type=payload.type,
        note=payload.note,
        start_date=payload.start_date,
        generate_count=payload.generate_count,
    )
    return {"success": True, "data": RecurringTransactionOut.model_validate(rule).model_dump(by_alias=True)}


@router.get("/recurring-transactions")
def list_recurring_transactions(db: Session = Depends(get_db)):
    service = RecurringTransactionService(db)
    rules = service.list_rules()
    return {
        "success": True,
        "data": [RecurringTransactionOut.model_validate(r).model_dump(by_alias=True) for r in rules],
    }


@router.put("/recurring-transactions/{rule_id}")
def update_recurring_transaction(rule_id: int, payload: RecurringTransactionInput, db: Session = Depends(get_db)):
    service = RecurringTransactionService(db)
    rule = service.update_rule(
        rule_id,
        frequency=payload.frequency,
        amount=payload.amount,
        category_id=payload.category_id,
        account_id=payload.account_id,
        type=payload.type,
        note=payload.note,
        start_date=payload.start_date,
        generate_count=payload.generate_count,
    )
    return {"success": True, "data": RecurringTransactionOut.model_validate(rule).model_dump(by_alias=True)}


@router.delete("/recurring-transactions/{rule_id}")
def delete_recurring_transaction(rule_id: int, db: Session = Depends(get_db)):
    service = RecurringTransactionService(db)
    service.delete_rule(rule_id)
    return {"success": True}


@router.post("/recurring-transactions/{rule_id}/generate")
def generate_recurring_transaction(rule_id: int, db: Session = Depends(get_db)):
    service = RecurringTransactionService(db)
    created = service.generate(rule_id)
    return {
        "success": True,
        "data": {
            "generatedCount": len(created),
            "transactions": [TransactionOut.model_validate(t).model_dump(by_alias=True) for t in created],
        },
    }
