from datetime import date

from sqlalchemy.orm import Session

from app.models.cloud_invoice import CloudInvoice, CloudInvoiceStatus
from app.models.cloud_invoice_sync_error import CloudInvoiceSyncError


class CloudInvoiceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        invoice_number: str,
        invoice_date: date,
        amount,
        seller_name: str,
        item_summary: str | None = None,
        status: CloudInvoiceStatus = CloudInvoiceStatus.PENDING_REVIEW,
        transaction_id: int | None = None,
    ) -> CloudInvoice:
        invoice = CloudInvoice(
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            amount=amount,
            seller_name=seller_name,
            item_summary=item_summary,
            status=status,
            transaction_id=transaction_id,
        )
        self.session.add(invoice)
        self.session.flush()
        return invoice

    def find(self, invoice_id: int) -> CloudInvoice | None:
        return self.session.get(CloudInvoice, invoice_id)

    def find_by_invoice_number(self, invoice_number: str) -> CloudInvoice | None:
        return (
            self.session.query(CloudInvoice)
            .filter(CloudInvoice.invoice_number == invoice_number)
            .one_or_none()
        )

    def find_pending_review(self) -> list[CloudInvoice]:
        return (
            self.session.query(CloudInvoice)
            .filter(CloudInvoice.status == CloudInvoiceStatus.PENDING_REVIEW)
            .order_by(CloudInvoice.id)
            .all()
        )

    def count_by_status(self) -> dict[CloudInvoiceStatus, int]:
        counts = {status: 0 for status in CloudInvoiceStatus}
        for invoice in self.session.query(CloudInvoice).all():
            counts[invoice.status] += 1
        return counts

    def latest_synced_at(self):
        return (
            self.session.query(CloudInvoice.created_at)
            .filter(CloudInvoice.status == CloudInvoiceStatus.SYNCED)
            .order_by(CloudInvoice.created_at.desc())
            .limit(1)
            .scalar()
        )

    def has_any(self) -> bool:
        return self.session.query(CloudInvoice).first() is not None or self.session.query(
            CloudInvoiceSyncError
        ).first() is not None

    def record_sync_error(self, *, invoice_number: str | None, error_message: str) -> None:
        self.session.add(CloudInvoiceSyncError(invoice_number=invoice_number, error_message=error_message))
        self.session.flush()

    def count_sync_errors(self) -> int:
        return self.session.query(CloudInvoiceSyncError).count()
