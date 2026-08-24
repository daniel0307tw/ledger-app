from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.budget import BudgetInput, BudgetOut, BudgetUpdateInput
from app.services.budget_service import BudgetService

router = APIRouter()


@router.post("/budgets", status_code=201)
def create_budget(payload: BudgetInput, db: Session = Depends(get_db)):
    service = BudgetService(db)
    budget = service.create_budget(
        scope=payload.scope, category_id=payload.category_id, monthly_amount=payload.monthly_amount
    )
    return {"success": True, "data": BudgetOut.model_validate(budget).model_dump(by_alias=True)}


@router.get("/budgets")
def list_budgets(db: Session = Depends(get_db)):
    service = BudgetService(db)
    budgets = service.list_budgets()
    return {"success": True, "data": [BudgetOut.model_validate(b).model_dump(by_alias=True) for b in budgets]}


# 必須在 /budgets/{budget_id} 之前註冊：兩者都是 GET，"status" 若落在 {budget_id} 之後註冊
# 會被當成 budget_id="status" 攔截，是本專案唯一真的存在方法相同、路徑會重疊的情況
# （budgets/{budget_id} 只掛 PUT/DELETE 這件事本身不會與 GET 衝突，這裡仍保留正確順序以防未來新增 GET /budgets/{id}）。
@router.get("/budgets/status")
def get_budget_status(db: Session = Depends(get_db)):
    service = BudgetService(db)
    return {"success": True, "data": service.get_status()}


@router.put("/budgets/{budget_id}")
def update_budget(budget_id: int, payload: BudgetUpdateInput, db: Session = Depends(get_db)):
    service = BudgetService(db)
    budget = service.update_budget(budget_id, monthly_amount=payload.monthly_amount)
    return {"success": True, "data": BudgetOut.model_validate(budget).model_dump(by_alias=True)}


@router.delete("/budgets/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    service = BudgetService(db)
    service.delete_budget(budget_id)
    return {"success": True}
