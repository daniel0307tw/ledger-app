from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.net_worth import NetWorthOut
from app.services.net_worth_service import NetWorthService

router = APIRouter()


@router.get("/net-worth")
def get_net_worth(db: Session = Depends(get_db)):
    service = NetWorthService(db)
    net_worth = service.get_net_worth()
    return {"success": True, "data": NetWorthOut(**net_worth).model_dump()}


@router.post("/net-worth/refresh")
def refresh_net_worth(db: Session = Depends(get_db)):
    service = NetWorthService(db)
    net_worth = service.refresh_net_worth()
    return {"success": True, "data": NetWorthOut(**net_worth).model_dump()}
