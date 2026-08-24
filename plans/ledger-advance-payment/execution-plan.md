# Execution Plan — ledger-advance-payment

## 2026-08-24 修正記錄：從「整筆代墊」改成「總金額中的一部分是代墊」

Phase 05/06 進行到 Chrome 實測時，使用者用實際案例（聚餐總額 4000，其中 1000 是自己
吃的、3000 是幫朋友代墊）指出原設計理解錯了：原設計假設一筆交易「整筆」要嘛是代墊款、
要嘛不是（`is_advance_payment` boolean + 全額排除），但實際需求是一筆交易的總金額
可能只有**一部分**是代墊款，結清後應該從支出統計扣掉代墊的那一部分（總金額－代墊金額），
而不是整筆排除為 0。

修正範圍：`is_advance_payment`（boolean）→ `advance_payment_amount`（nullable decimal，
交易總金額中屬於代墊款的部分，等於總金額時就是原本「整筆代墊」的特例）。已回頭修正
Phase 01（`系統抽象.md`、7 個 feature 檔）、Phase 02（`erm.dbml`）、Phase 04（`api.yml`）
的產出物本身（不是新增一輪 Discovery，因為變動範圍明確、屬於同一個欄位設計的修正，
不是新的行為需求），Phase 01-04 卡片維持在 `done/` 不重跑；Phase 05/06 因為程式碼已經
照舊模型寫完，卡片移回 `doing/` 重新實作。Phase 07 尚未開始，不受影響。

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 4 |
| Modify | 6 |

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `ledger_transaction` table | 新增 3 欄位：`is_advance_payment`（boolean, default false）、`advance_payment_status`（nullable enum: pending/settled）、`settlement_transaction_id`（nullable FK → ledger_transaction.id，單向，比照 `source_recurring_transaction_id` 的 FK 模式而非 `transfer_group_id` 的無 FK 字串關聯） |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `transactions/新增收支紀錄.feature` | 新增 Rule：`isAdvancePayment` 僅限 type=支出，type=收入 時標記則拒絕 |
| modify | `transactions/編輯收支紀錄.feature` | 新增 Rule：編輯已結清代墊交易的金額，允許編輯但自動取消結清（狀態改回 pending，解除與還款交易的關聯） |
| modify | `transactions/刪除收支紀錄.feature` | 新增 Rule：刪除「還款交易」時，原代墊交易的已結清狀態復原為未結清 |
| create | `transactions/確認收到還款.feature` | 新 command：對代墊款交易確認收到還款——建立對應收入交易 + 標記原交易已結清；含金額不符拒絕、已結清/非代墊款/不存在等錯誤情境 |
| create | `transactions/查詢待收回代墊款清單.feature` | 新 query：列出所有未結清的代墊款交易 |
| modify | `budgets/查詢預算執行狀況.feature` | 新增 Rule：已結清代墊交易不計入預算花費統計，比照既有 is_transfer 排除 Rule |
| modify | `reports/查詢分類花費統計.feature` | 新增 Rule：已結清代墊交易不計入分類花費統計，比照既有 is_transfer 排除 Rule |

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `TransactionInput` | 新增選填欄位 `isAdvancePayment: boolean` |
| modify | `Transaction`（輸出 schema） | 新增 `isAdvancePayment`、`advancePaymentStatus`、`settlementTransactionId` |
| create | `POST /api/transactions/{id}/settle-advance-payment` | 確認收到還款；body：`{ date, amount, accountId }` |
| create | `GET /api/transactions/advance-payments/pending` | 查詢待收回代墊款清單 |

## Phase 05-07: Implementation

| 操作 | 目標 | 說明 |
|------|------|------|
| red-green-refactor | 上述新建/修改的 6 個 .feature | 依標準 TDD 循環實作 |
| frontend | 交易表單 + 交易列表 + 新增「待收回代墊款」頁面/區塊 | Phase 06 依 Feature Examples 與 api.yml 建置 |

## 已確認的設計決策（Clarify Loop 收斂結果）

1. 已結清代墊交易若編輯金額 → 允許編輯，但自動取消結清（狀態回 pending，`settlement_transaction_id` 清空）；已建立的還款收入交易本身不連動刪除，維持獨立紀錄，由使用者自行處理
2. `isAdvancePayment=true` 但 `type=收入` → 拒絕，回傳驗證錯誤
3. 新增「查詢待收回代墊款清單」query 功能
4. 還款入帳帳戶無預設值，`accountId` 為必填參數，比照新增收支紀錄的既有慣例

## IMPL_IMPACT（由 Phase 02-04 回填）

| Phase | 影響目標 | Impact Type | 來源 | 說明 |
|-------|---------|-------------|------|------|
| 05 | `app/models/ledger_transaction.py` | FIELD_CHANGE | Phase 02 | +is_advance_payment, +advance_payment_status, +settlement_transaction_id |
| 05 | `alembic/versions/` | FIELD_CHANGE | Phase 02 | migration 新增 3 欄位 |
| 05 | `app/repositories/transaction_repository.py` | QUERY_FILTER_CHANGE | Phase 01 | 三處 EXPENSE 加總查詢加上「已結清代墊交易排除」條件 |
| 05 | `app/services/transaction_service.py` | NEW_OPERATION | Phase 01 | settle-advance-payment 邏輯、刪除還款交易時復原狀態、編輯已結清交易時取消結清 |
| 06 | `web/src/mocks/handlers/` | ENDPOINT_SCHEMA | Phase 04 | 新增 settle-advance-payment、pending 清單 handler |
| 06 | `web/src/app/transactions/` | ENDPOINT_SCHEMA | Phase 04 | 交易表單加代墊款標記、清單加「確認收到還款」動作、新增待收回清單頁面 |
| 07 | — | auto | Phase 05/06 | 有變動則重跑整合驗證 |
