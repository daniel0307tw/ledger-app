from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.account import AccountType
from app.schemas.account import AccountInput, AccountOut
from app.services.account_service import AccountService

router = APIRouter()


@router.post("/accounts", status_code=201)
def create_account(payload: AccountInput, db: Session = Depends(get_db)):
    service = AccountService(db)
    account = service.create_account(name=payload.name, type=AccountType(payload.type))
    return {"success": True, "data": AccountOut.model_validate(account).model_dump(by_alias=True)}


@router.get("/accounts")
def list_accounts(db: Session = Depends(get_db)):
    service = AccountService(db)
    accounts = service.list_accounts()
    return {
        "success": True,
        "data": [AccountOut.model_validate(a).model_dump(by_alias=True) for a in accounts],
    }
