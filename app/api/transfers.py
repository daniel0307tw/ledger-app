from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.transaction import TransactionOut
from app.schemas.transfer import TransferInput
from app.services.transfer_service import TransferService

router = APIRouter()


@router.post("/transfers", status_code=201)
def create_transfer(payload: TransferInput, db: Session = Depends(get_db)):
    service = TransferService(db)
    outgoing, incoming = service.create_transfer(
        from_account_id=payload.from_account_id,
        to_account_id=payload.to_account_id,
        amount=payload.amount,
        date=payload.date,
    )
    return {
        "success": True,
        "data": [
            TransactionOut.model_validate(outgoing).model_dump(by_alias=True),
            TransactionOut.model_validate(incoming).model_dump(by_alias=True),
        ],
    }
