from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.category import CategoryType
from app.schemas.category import CategoryInput, CategoryOut
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("/categories", status_code=201)
def create_category(payload: CategoryInput, db: Session = Depends(get_db)):
    service = CategoryService(db)
    category = service.create_category(name=payload.name, type=CategoryType(payload.type))
    return {"success": True, "data": CategoryOut.model_validate(category).model_dump(by_alias=True)}


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    service = CategoryService(db)
    categories = service.list_categories()
    return {
        "success": True,
        "data": [CategoryOut.model_validate(c).model_dump(by_alias=True) for c in categories],
    }
