from datetime import date as date_type
from decimal import Decimal, InvalidOperation

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.cloud_invoice import CloudInvoice, CloudInvoiceStatus
from app.repositories.account_repository import AccountRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.cloud_invoice_repository import CloudInvoiceRepository
from app.repositories.transaction_repository import TransactionRepository
from app.services.category_classifier import classify_category
from app.services.transaction_service import TransactionService

DEFAULT_ACCOUNT_NAME = "現金"
DEFAULT_CATEGORY_NAME = "日常用品"
REQUIRED_FIELDS = ("invoiceNumber", "invoiceDate", "amount", "sellerName")


class CloudInvoiceService:
    def __init__(self, session: Session):
        self.session = session
        self.cloud_invoices = CloudInvoiceRepository(session)
        self.transactions = TransactionRepository(session)
        self.accounts = AccountRepository(session)
        self.categories = CategoryRepository(session)
        self.transaction_service = TransactionService(session)

    def _default_account_id(self) -> int:
        account = self.accounts.find_by_name(DEFAULT_ACCOUNT_NAME)
        if account is None:
            raise NotFoundError(f"找不到預設帳戶「{DEFAULT_ACCOUNT_NAME}」")
        return account.id

    def _default_category_id(self) -> int:
        category = self.categories.find_by_name(DEFAULT_CATEGORY_NAME)
        if category is None:
            raise NotFoundError(f"找不到預設分類「{DEFAULT_CATEGORY_NAME}」")
        return category.id

    def _resolve_category_id(
        self, seller_name: str, item_summary: str | None, suggested_category_id: int | None
    ) -> int:
        """分類判斷優先順序：關鍵字比對（高信心）→ Hermes 建議分類（LLM 判斷，信心較低但
        比預設值準）→ 預設分類「日常用品」（兩者都沒有時的最後防線）。"""
        classified_name = classify_category(seller_name, item_summary)
        if classified_name is not None:
            category = self.categories.find_by_name(classified_name)
            if category is not None:
                return category.id
        if suggested_category_id is not None:
            category = self.categories.find(suggested_category_id)
            if category is not None:
                return category.id
        return self._default_category_id()

    def _validate_item(self, item: dict) -> str | None:
        """回傳缺漏欄位的錯誤訊息；資料完整則回傳 None。"""
        missing = [f for f in REQUIRED_FIELDS if not item.get(f) and item.get(f) != 0]
        if missing:
            return f"缺少必要欄位：{', '.join(missing)}"
        try:
            amount = Decimal(str(item["amount"]))
        except (InvalidOperation, TypeError, ValueError):
            return "amount 格式錯誤"
        if amount <= 0:
            return "amount 必須為正數"
        try:
            date_type.fromisoformat(str(item["invoiceDate"]))
        except ValueError:
            return "invoiceDate 格式錯誤"
        return None

    def sync_invoices(self, items: list[dict]) -> list[dict]:
        results = []
        for item in items:
            invoice_number = item.get("invoiceNumber")
            error = self._validate_item(item)
            if error is not None:
                self.cloud_invoices.record_sync_error(invoice_number=invoice_number, error_message=error)
                results.append(
                    {"invoiceNumber": invoice_number, "result": "invalid", "errorMessage": error}
                )
                continue

            existing = self.cloud_invoices.find_by_invoice_number(invoice_number)
            if existing is not None:
                results.append({"invoiceNumber": invoice_number, "result": "skipped"})
                continue

            invoice_date = date_type.fromisoformat(item["invoiceDate"])
            amount = Decimal(str(item["amount"]))
            seller_name = item["sellerName"]
            item_summary = item.get("itemSummary")

            similar = self.transactions.find_by_date_and_amount(invoice_date, amount)
            if similar is not None:
                self.cloud_invoices.create(
                    invoice_number=invoice_number,
                    invoice_date=invoice_date,
                    amount=amount,
                    seller_name=seller_name,
                    item_summary=item_summary,
                    status=CloudInvoiceStatus.PENDING_REVIEW,
                )
                results.append({"invoiceNumber": invoice_number, "result": "pending_review"})
                continue

            transaction = self.transaction_service.create_transaction(
                date=invoice_date,
                amount=amount,
                category_id=self._resolve_category_id(seller_name, item_summary, item.get("categoryId")),
                account_id=self._default_account_id(),
                type="支出",
                note=f"{seller_name} {item_summary}".strip() if item_summary else seller_name,
            )
            self.cloud_invoices.create(
                invoice_number=invoice_number,
                invoice_date=invoice_date,
                amount=amount,
                seller_name=seller_name,
                item_summary=item_summary,
                status=CloudInvoiceStatus.SYNCED,
                transaction_id=transaction.id,
            )
            results.append(
                {"invoiceNumber": invoice_number, "result": "created", "transactionId": transaction.id}
            )
        self.session.flush()
        return results

    def list_pending(self) -> list[CloudInvoice]:
        return self.cloud_invoices.find_pending_review()

    def find_similar_for(self, invoice: CloudInvoice):
        return self.transactions.find_by_date_and_amount(invoice.invoice_date, invoice.amount)

    def confirm(
        self,
        invoice_id: int,
        *,
        decision: str,
        account_id: int | None = None,
        category_id: int | None = None,
    ) -> CloudInvoice:
        invoice = self.cloud_invoices.find(invoice_id)
        if invoice is None:
            raise NotFoundError("找不到該筆雲端發票")
        if invoice.status != CloudInvoiceStatus.PENDING_REVIEW:
            raise BusinessError("此筆發票已處理過")

        if decision == "confirm_duplicate":
            invoice.status = CloudInvoiceStatus.SKIPPED
            self.session.flush()
            return invoice

        transaction = self.transaction_service.create_transaction(
            date=invoice.invoice_date,
            amount=invoice.amount,
            category_id=category_id or self._default_category_id(),
            account_id=account_id or self._default_account_id(),
            type="支出",
            note=f"{invoice.seller_name} {invoice.item_summary}".strip()
            if invoice.item_summary
            else invoice.seller_name,
        )
        invoice.status = CloudInvoiceStatus.SYNCED
        invoice.transaction_id = transaction.id
        self.session.flush()
        return invoice

    def get_health(self) -> dict:
        has_history = self.cloud_invoices.has_any()
        counts = self.cloud_invoices.count_by_status()
        return {
            "hasSyncHistory": has_history,
            "lastSyncedAt": self.cloud_invoices.latest_synced_at(),
            "pendingCount": counts[CloudInvoiceStatus.PENDING_REVIEW],
            "syncedCount": counts[CloudInvoiceStatus.SYNCED],
            "errorCount": self.cloud_invoices.count_sync_errors(),
        }
