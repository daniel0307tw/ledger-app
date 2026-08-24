from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.schemas.cloud_invoice import CloudInvoiceOut, ConfirmCloudInvoiceInput, SimilarTransactionOut
from app.services.cloud_invoice_service import CloudInvoiceService

router = APIRouter()


@router.post("/cloud-invoices/sync")
async def sync_cloud_invoices(request: Request, db: Session = Depends(get_db)):
    items = await request.json()
    service = CloudInvoiceService(db)
    results = service.sync_invoices(items)
    return {"success": True, "data": results}


@router.get("/cloud-invoices/pending")
def list_pending_cloud_invoices(db: Session = Depends(get_db)):
    service = CloudInvoiceService(db)
    invoices = service.list_pending()
    data = []
    for invoice in invoices:
        similar = service.find_similar_for(invoice)
        out = CloudInvoiceOut.model_validate(invoice)
        if similar is not None:
            out.similar_transaction = SimilarTransactionOut.model_validate(similar)
        data.append(out.model_dump(by_alias=True))
    return {"success": True, "data": data}


@router.post("/cloud-invoices/{invoice_id}/confirm")
def confirm_cloud_invoice(invoice_id: int, payload: ConfirmCloudInvoiceInput, db: Session = Depends(get_db)):
    service = CloudInvoiceService(db)
    invoice = service.confirm(
        invoice_id,
        decision=payload.decision,
        account_id=payload.account_id,
        category_id=payload.category_id,
    )
    return {"success": True, "data": CloudInvoiceOut.model_validate(invoice).model_dump(by_alias=True)}


@router.get("/cloud-invoices/health")
def get_cloud_invoice_health(db: Session = Depends(get_db)):
    service = CloudInvoiceService(db)
    return {"success": True, "data": service.get_health()}
