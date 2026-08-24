# Phase 05: Backend TDD Track

## 審查進度

- [x] 05.1 相關規格已審查 — **簽名**: 2026-08-24 22:15
- [x] 05.2 交付物已審查 — **簽名**: 2026-08-24 22:15

## 修正記錄（2026-08-24 22:15）

**背景**：Phase 05 第一輪實作誤用了「代墊款」的資料模型——用單一 boolean `is_advance_payment` 表達
「這筆交易是否整筆都是代墊款」，無法表達「一筆交易裡一部分是自己的消費、一部分是幫別人代墊」的混合情境
（例如聚餐總額 4000，其中 3000 代墊、1000 自己吃）。規格已修正為 `advance_payment_amount`（nullable
decimal，交易金額中屬於代墊款的部分），本輪逐一修正下列已實作的檔案，使其與修正後的 `specs/erm.dbml`、
`specs/api.yml`、7 個 `.feature` 檔案（已修正為 ground truth）一致：

- `app/models/ledger_transaction.py`：`is_advance_payment: bool` 欄位 → `advance_payment_amount: float | None`
  （`Numeric(14,4)` nullable）。`AdvancePaymentStatus` enum 形狀不變。
- `alembic/versions/006_add_advance_payment_to_ledger_transaction.py`：**直接在原檔案上修改**（未新增
  migration）——upgrade/downgrade 都改為 `advance_payment_amount NUMERIC(14,4) NULL` 取代原本的
  `is_advance_payment BOOLEAN NOT NULL DEFAULT false`。理由：確認過 `alembic current` 顯示 DB 停在 005，
  `\d ledger_transaction` 也確認 006 新增的三個欄位在 DB 裡完全不存在——該 migration 從未被
  `alembic upgrade head` 套用過，此功能也還沒上線，故直接修改比疊加一個修正用的新 migration 更乾淨。
  已實際跑過 `alembic upgrade head` → 確認欄位型別正確（`advance_payment_amount numeric(14,4)`，
  nullable）→ `alembic downgrade -1` 驗證可乾淨回退 → 再次 `upgrade head`，最終 DB 停在 006（head）。
- `app/schemas/transaction.py`：`TransactionInput`/`TransactionOut` 的 `isAdvancePayment: bool` →
  `advancePaymentAmount: float | None`（alias 對應 api.yml）。`SettleAdvancePaymentInput` 形狀不變。
- `app/repositories/transaction_repository.py`：**核心修正**——`_not_settled_advance_payment()`（WHERE
  子句排除整筆）改為 `_effective_amount()`（SUM 內的 CASE 部分扣除），套用到 `sum_amount_in_range`、
  `sum_amount_by_category_in_range`、`sum_amount_by_category` 三個方法。另外 `create()`、
  `find_settlement_source`、`find_pending_advance_payments` 的參數/篩選條件改用
  `advance_payment_amount is not None` 取代 `is_advance_payment is True`。
- `app/services/transaction_service.py`：`create_transaction` 新增「代墊金額不可超過交易總金額」422 檢查
  （沿用既有「代墊款標記僅限支出交易」檢查順序）；`update_transaction` 新增 `advance_payment_amount` 參數
  與相同的兩項驗證，且「已結清自動改回未結清」的判斷從只看 `amount` 變動改為看 `amount` **或**
  `advance_payment_amount` 任一變動；`settle_advance_payment` 的檢查與建立金額改為對比/採用
  `transaction.advance_payment_amount`（而非 `transaction.amount`）。
- `app/api/transactions.py`：create/update handler 改傳 `payload.advance_payment_amount`。
- `tests/features/steps/transactions_steps.py`：`Given`/`When`/`Then` 步驟的 `isAdvancePayment` 布林解析
  → `advancePaymentAmount` 數字解析（空字串＝null，比照既有其他選填數字欄位的慣例）；「查詢待收回代墊款清單」
  的 Then 步驟加入 `advancePaymentAmount` 欄位比對；「操作成功，結果符合」的布林分支改為數字分支。
- `tests/features/steps/budgets_steps.py`：`Given` 步驟同樣的欄位改名與型別修正。

### 核心 SQL：SUM 查詢的部分扣除 CASE 表達式

```python
def _effective_amount():
    """支出/預算/報表加總時實際計入的金額：已結清（advance_payment_amount 不為 null 且
    advance_payment_status=settled）的代墊款交易，有效金額為 amount − advance_payment_amount
    （而非排除整筆、也不是 0）；尚未結清或非代墊款交易仍以 amount 全額計入。"""
    return case(
        (
            and_(
                LedgerTransaction.advance_payment_amount.isnot(None),
                LedgerTransaction.advance_payment_status == AdvancePaymentStatus.SETTLED,
            ),
            LedgerTransaction.amount - LedgerTransaction.advance_payment_amount,
        ),
        else_=LedgerTransaction.amount,
    )
```

`func.sum(_effective_amount())` 取代原本 `func.sum(LedgerTransaction.amount)` + WHERE 排除整筆的寫法，
套用於 `sum_amount_in_range`、`sum_amount_by_category_in_range`、`sum_amount_by_category`（含其
`ORDER BY func.sum(_effective_amount()).desc()`，因為 `func.sum(LedgerTransaction.amount)` 已不再是查詢中
實際使用的加總欄位，排序表達式須同步替換，否則會對到未使用的欄位）。已用 `查詢預算執行狀況.feature` 與
`查詢分類花費統計.feature` 的具體 Example（總額 4000／代墊 3000／settled → 有效金額 1000；總額 4000／代墊
3000／pending → 有效金額 4000）驗證通過。

## 目的 (What)

以 Phase 01-04 的產出為輸入，
對每個 .feature 執行完整 TDD 三階段循環（Red → Green → Refactor），直到所有 BDD 測試通過。

**雙模式運作**：依 Execution Plan 的 IMPL_IMPACT 決定走哪種模式。

| 模式 | 觸發條件 | 行為 |
|------|---------|------|
| **One-shot TDD** | 該 feature 的 IMPL_IMPACT 只有 `NEW_OPERATION` 或無 | 完整 Red → Green → Refactor |
| **Targeted Fix** | 該 feature 有具體 impact type（`SENTENCE_PATTERN` / `DATATABLE_SCHEMA` / `FIELD_CHANGE` 等） | 定位受影響的 implementation artifact → 定向修復 → 回歸測試 |

觸發 skill：`/aibdd-auto-control-flow`（內部自動從 arguments.yml 路由語言變體）
control-flow 內部有 N features × 3 phases 的 TodoWrite，自管進度。

**依賴**：Phase 04 必須在 `done/` 中。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | Execution Plan | Phase 01 交付 | 本 Phase 的工作範圍（哪些 feature 需 TDD） |
| 2 | api.yml | Phase 04 交付 | API 契約（欄位名、envelope、error code） |
| 3 | erm.dbml | Phase 02 交付 | Entity 結構 |
| 4 | Feature Files | Phase 03 交付 | 可執行規格（含 Examples） |

## 交付物

carry-on Step 05.2 觸發時：

1. 讀取 Execution Plan 的 IMPL_IMPACT（Phase 05 區段）
2. 對每個 .feature 判斷模式：

### One-shot TDD（正常模式）

**DELEGATE `/aibdd-auto-control-flow`**，對每個 new feature 依序走：

| Phase | Skill | 做什麼 |
|-------|-------|--------|
| Red | `/aibdd-auto-red` | Schema Analysis → Step Template → 寫 E2E 測試（欄位名 = api.yml） |
| Green | `/aibdd-auto-green` | 實作至測試通過 |
| Refactor | `/aibdd-auto-refactor` | 程式碼品質提升 |

### Targeted Fix（定向修復模式）

對每個有具體 IMPL_IMPACT 的 feature：

| Impact Type | 修復動作 |
|-------------|---------|
| `SENTENCE_PATTERN` | 定位 Step Def → 更新 pattern/regex 匹配新句型 → 跑單一 feature 測試 |
| `DATATABLE_SCHEMA` | 定位 Step Def → 更新 DataTable 解析邏輯（加/刪欄位）→ 跑測試 |
| `FIELD_CHANGE` | 更新 Domain Model + 產生 Migration → 跑測試 |
| `ENUM_CHANGE` | 更新 Domain Model enum 定義 → 跑測試 |
| `ENDPOINT_SCHEMA` | 更新 Endpoint handler（request 解析 / response 序列化）→ 跑測試 |
| `ENDPOINT_ROUTE` | 更新 route decorator + URL path → 跑測試 |

每個 Skill 內部自動讀取 arguments.yml → 載入對應語言變體的 reference。

3. 全部完成後執行回歸測試（**包含未修改的 feature，確認無級聯破壞**）

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 05.1 | Step Definitions | `/home/daniel/dev/ledger-app/tests/features/steps/transactions_steps.py`（modify：`isAdvancePayment` → `advancePaymentAmount`）、`/home/daniel/dev/ledger-app/tests/features/steps/budgets_steps.py`（modify：同上） | DONE |
| 05.2 | Domain Models | `/home/daniel/dev/ledger-app/app/models/ledger_transaction.py`（modify：`is_advance_payment: bool` → `advance_payment_amount: float \| None`）、`/home/daniel/dev/ledger-app/app/models/__init__.py`（無需改動，`AdvancePaymentStatus` export 不變） | DONE |
| 05.3 | API Endpoints | `/home/daniel/dev/ledger-app/app/api/transactions.py`（modify：create/update handler 改傳 `payload.advance_payment_amount`） | DONE |
| 05.4 | DB Migrations | `/home/daniel/dev/ledger-app/alembic/versions/006_add_advance_payment_to_ledger_transaction.py`（**直接修改既有檔案**，未新增新 migration；理由見上方「修正記錄」） | DONE |
| 05.5 | 回歸測試結果 | 回歸測試全通過（見下方「補充：實作細節」） | DONE |

其餘修改（Schema / Repository / Service 層，交付物表格未逐一列出但屬於本 Phase 範圍）：
- `/home/daniel/dev/ledger-app/app/schemas/transaction.py`（modify：`isAdvancePayment: bool` → `advancePaymentAmount: float \| None`）
- `/home/daniel/dev/ledger-app/app/repositories/transaction_repository.py`（modify：三個 `sum_*` 方法改為 CASE 部分扣除，見上方核心 SQL；`create()`/`find_settlement_source`/`find_pending_advance_payments` 改用新欄位）
- `/home/daniel/dev/ledger-app/app/services/transaction_service.py`（modify：`create_transaction`/`update_transaction` 加代墊金額驗證（僅限支出、不可超過總金額）；`update_transaction` 的已結清自動復原判斷改為看 `amount` 或 `advance_payment_amount` 任一變動；`settle_advance_payment` 改對比/採用 `advance_payment_amount`）

### 驗收點

- [x] 所有 .feature × 3 phase 任務 completed
- [x] 回歸測試全數通過（零失敗）
- [x] Migration 006 已針對真實 dev DB 驗證：`alembic upgrade head`（005→006 成功）→ `\d ledger_transaction` 確認欄位型別正確 → `alembic downgrade -1`（006→005 成功）→ 再次 `upgrade head`，最終停在 006 (head)

### 補充：實作細節

**修正後全量回歸測試結果**（`.venv/bin/behave tests/features/ --tags=~@ignore`，2026-08-24 22:15）：
`27 features passed, 0 failed, 0 skipped` / `117 scenarios passed, 0 failed, 0 skipped` / `435 steps passed, 0 failed, 0 skipped`。
（原始第一輪為 27/113/420；本輪修正後場景數與步驟數增加，因 `編輯收支紀錄.feature` 新增了「編輯代墊金額後自動取消結清」的 Example，且既有 step 定義擴充了 `advancePaymentAmount` 欄位比對邏輯。）

**執行順序**：依卡片指示，先做 新增/編輯/刪除收支紀錄（建立 DB 欄位與基礎驗證）→ 確認收到還款 → 查詢待收回代墊款清單 → 預算執行狀況／分類花費統計（純查詢過濾，重用 repository 排除條件即通過）。逐一以 `.venv/bin/behave <單一 feature>` 跑到綠燈後才進下一個，最後做全量回歸。

**值得記錄的實作決策**（皆在規格允許的空間內、非偏離規格）：
1. `TransactionService.create_transaction`（及 `update_transaction`）中，`advance_payment_amount is not None`（僅限支出）的檢查刻意放在 `_assert_category_type_matches` **之前**——因為 Example「標記代墊款用於收入交易時操作失敗」用的分類（餐飲）本身是支出分類，若先做分類類型比對會被既有的「分類收支類型與交易類型不符」攔截，訊息就對不上規格要求的「代墊款標記僅限支出交易」。「代墊金額不可超過交易總金額」的檢查緊接在其後。
2. `settle_advance_payment` 建立還款收入交易時，直接呼叫 `TransactionRepository.create(category_id=None, ...)`，比照 `TransferService.create_transfer` 的既有模式，而非呼叫 `TransactionService.create_transaction()`——因為 `SettleAdvancePaymentInput`（api.yml）沒有 `categoryId` 欄位，`create_transaction()` 會強制要求分類存在，不適用。CashPosition 同步仍重用 `sync_to_cash_position()`，符合「同一套失敗容忍同步慣例」的要求。
3. `delete_transaction` 刪除「還款交易」時，**先**清空原代墊款交易的 `settlement_transaction_id` 並 flush，**再**刪除該筆——避免撞上自參考 FK 約束（即使該 FK 已加 `ondelete=SET NULL` 作為資料庫層防線，service 層仍需要明確處理才能同時把 `advance_payment_status` 復原為 pending）。
4. 既有共用 step `Then 應建立一筆收支紀錄：`（`transactions_steps.py`）因應「確認收到還款」的回應是巢狀 `{settlementTransaction, advancePaymentTransaction}` 結構，改為偵測 `data` 中是否有 `settlementTransaction` 鍵並取用；同時 `category` 欄位比對改為僅在 Data Table 有該欄位時才檢查（確認收到還款的 Table 沒有 `category` 欄）。此步驟原本被既有 `新增收支紀錄.feature` 使用，改動後兩處都持續通過。
5. `Then 操作成功，結果符合：` 的 `isAdvancePayment` 布林比對分支改為 `advancePaymentAmount` 數字比對分支（空字串期望值＝null，實際值轉 float 後比較，避免 `"3000" != "3000.0"` 之類的字串誤判）。
6.（本輪修正新增）`update_transaction` 原本完全不接受代墊款相關參數（第一輪的已知缺口，見「編輯頁不顯示代墊款欄位」的舊決策）；本輪修正後改為接受 `advance_payment_amount`，並套用與 `create_transaction` 相同的兩項驗證（僅限支出、不可超過總金額），使 `編輯收支紀錄.feature` 的「編輯已結清代墊款交易的代墊金額後自動取消結清」Example 得以通過。
7.（本輪修正新增）「查詢待收回代墊款清單」的 Then 步驟原本只比對 `date/amount/categoryId/accountId` 四個欄位，未比對 Example 表格中的 `advancePaymentAmount` 欄位；本輪修正後加入該欄位比對（空字串→None），確保清單回應確實回傳正確的代墊金額而非只回傳筆數/其他欄位正確。

**未發現需要偏離規格之處**：erm.dbml / api.yml / 7 個 .feature 檔案的欄位名、錯誤訊息、Rule 順序、回應結構皆照字面實作，未做任何規格外的改動或簡化。
