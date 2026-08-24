from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.report import CategorySummaryOut
from app.schemas.transaction import TransactionOut
from app.services.report_service import ReportService

router = APIRouter()


@router.get("/reports/category-summary")
def get_category_summary(startDate: date, endDate: date, db: Session = Depends(get_db)):
    service = ReportService(db)
    summary = service.get_category_summary(startDate, endDate)
    return {
        "success": True,
        "data": [
            CategorySummaryOut(category=category, total_amount=total_amount).model_dump(by_alias=True)
            for category, total_amount in summary
        ],
    }


@router.get("/reports/category-detail")
def get_category_detail(category: str, startDate: date, endDate: date, db: Session = Depends(get_db)):
    service = ReportService(db)
    transactions = service.get_category_detail(category, startDate, endDate)
    return {
        "success": True,
        "data": [TransactionOut.model_validate(t).model_dump(by_alias=True) for t in transactions],
    }
