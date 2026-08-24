from app.models.ledger_transaction import LedgerTransaction, SyncStatus, TransactionType
from app.repositories.cash_position_repository import CashPositionRepository, CashPositionSyncError

CURRENCY = "TWD"

_CASH_TYPE_BY_TRANSACTION_TYPE = {
    TransactionType.EXPENSE: "Withdraw",
    TransactionType.INCOME: "Deposit",
}


def sync_to_cash_position(
    cash_positions: CashPositionRepository, transaction: LedgerTransaction, institution: str
) -> None:
    """嘗試將交易同步寫入外部 CashPosition。成功則標記 synced，失敗則標記 pending，不拋出例外。"""
    cash_type = _CASH_TYPE_BY_TRANSACTION_TYPE[TransactionType(transaction.type)]
    try:
        cash_position_id = cash_positions.create(
            institution=institution, amount=transaction.amount, currency=CURRENCY, type=cash_type
        )
    except CashPositionSyncError:
        transaction.sync_status = SyncStatus.PENDING
        transaction.cash_position_id = None
        return
    transaction.sync_status = SyncStatus.SYNCED
    transaction.cash_position_id = cash_position_id


def cancel_previous_sync(cash_positions: CashPositionRepository, transaction: LedgerTransaction) -> None:
    """取消先前的同步結果：若已同步成功，刪除對應的 CashPosition 那筆；若仍待重試，無事可做。"""
    if transaction.sync_status == SyncStatus.SYNCED and transaction.cash_position_id is not None:
        try:
            cash_positions.delete(transaction.cash_position_id)
        except CashPositionSyncError:
            pass
    transaction.sync_status = SyncStatus.PENDING
    transaction.cash_position_id = None
