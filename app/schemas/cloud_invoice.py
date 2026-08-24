from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class CloudInvoiceSyncItem(BaseModel):
    invoice_number: str = Field(alias="invoiceNumber")
    invoice_date: date = Field(alias="invoiceDate")
    amount: float = Field(gt=0)
    seller_name: str = Field(alias="sellerName")
    item_summary: str | None = Field(default=None, alias="itemSummary")

    model_config = {"populate_by_name": True}


class CloudInvoiceSyncResult(BaseModel):
    invoice_number: str = Field(serialization_alias="invoiceNumber")
    result: Literal["created", "pending_review", "skipped", "invalid"]
    transaction_id: int | None = Field(default=None, serialization_alias="transactionId")
    error_message: str | None = Field(default=None, serialization_alias="errorMessage")

    model_config = {"from_attributes": True}


class SimilarTransactionOut(BaseModel):
    id: int
    date: date
    amount: float
    note: str | None

    model_config = {"from_attributes": True}


class CloudInvoiceOut(BaseModel):
    id: int
    invoice_number: str = Field(serialization_alias="invoiceNumber")
    invoice_date: date = Field(serialization_alias="invoiceDate")
    amount: float
    seller_name: str = Field(serialization_alias="sellerName")
    item_summary: str | None = Field(serialization_alias="itemSummary")
    status: str
    transaction_id: int | None = Field(serialization_alias="transactionId")
    similar_transaction: SimilarTransactionOut | None = Field(default=None, serialization_alias="similarTransaction")

    model_config = {"from_attributes": True}


class ConfirmCloudInvoiceInput(BaseModel):
    decision: Literal["confirm_new", "confirm_duplicate"]
    account_id: int | None = Field(default=None, alias="accountId")
    category_id: int | None = Field(default=None, alias="categoryId")

    model_config = {"populate_by_name": True}


class CloudInvoiceHealthOut(BaseModel):
    has_sync_history: bool = Field(serialization_alias="hasSyncHistory")
    last_synced_at: datetime | None = Field(serialization_alias="lastSyncedAt")
    pending_count: int = Field(serialization_alias="pendingCount")
    synced_count: int = Field(serialization_alias="syncedCount")
    error_count: int = Field(serialization_alias="errorCount")
