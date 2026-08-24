# Execution Plan — ledger-category

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 7（category table、2 個新 Feature、1 個新 Activity、2 個新 endpoint、前端分類選擇/新增元件） |
| Modify | 6（ledger_transaction.category 欄位、TransactionInput/Transaction schema、4 個 transactions Feature 補分類存在性 Rule、TransactionForm.tsx） |
| Delete | 0 |

## Structural Read 摘要（既有系統現狀）

| Artifact | 現狀 |
|---|---|
| `specs/erm.dbml` | `account`(id,name)、`ledger_transaction`(...,`category`:varchar not null,...)，`category` 目前無關聯、無實體 |
| `specs/api.yml` | 7 endpoints；`TransactionInput`/`Transaction` schema 的 `category` 是 `string` |
| `tests/features/accounts/` | 建立帳戶.feature、查詢帳戶列表.feature — **本輪 category 的 CRUD 直接複用這兩個檔案的 Rule 結構模式**（帳戶名稱不強制唯一 → 分類名稱比照辦理） |
| `tests/features/transactions/` | 4 個檔案（新增/編輯/刪除/查詢），`category` 欄位在所有 datatable 中都以字串形式出現（如「餐飲」「交通」），且既有範例值都落在使用者提供的 17 個預設分類內 → **既有 Example 資料不需更動**，只需新增「分類不存在」的失敗 Rule（比照既有「帳戶不存在」Rule 的寫法） |
| `specs/activities/` | 2 個檔案，皆無「選分類」子流程；`帳戶管理與轉帳.mmd` 有「查詢帳戶列表」作為獨立支援性 STEP 的先例 → 本輪比照建立獨立的「分類管理.mmd」 |
| `web/src/components/TransactionForm.tsx` | 分類欄位目前是自由文字 `<input>` + `<datalist>`（`CATEGORY_SUGGESTIONS` 常數），要改成參照分類實體的選擇/新增元件 |

## 待確認的推論（ASM，已用「GO」確認方向，本輪依此執行；Feedback Loop 時仍可推翻）

- `ASM-1`：`ledger_transaction.category` 從 varchar 改成 `category_id` FK
- `ASM-2`：記帳表單裡新增的分類直接可選用於當前這筆紀錄
- `ASM-3`（新增）：分類名稱**不強制唯一**，比照 `account.name` 的既有慣例（`帳戶名稱使用者自訂...不強制唯一`）——使用者未提及分類唯一性，選擇與既有 account 慣例一致的最小驚訝設計

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|---|---|---|
| create | `category` table | `id`(pk), `name`(varchar, not null, not unique，比照 account) |
| modify | `ledger_transaction.category` | varchar → `category_id`(integer, FK → category.id, not null) |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|---|---|---|
| create | `categories/` domain | 查詢分類列表.feature、建立分類.feature 補 Examples（含 17 個預設分類的查詢結果驗證） |
| modify | `transactions/新增收支紀錄.feature` | 新增 Rule「分類不存在時操作失敗」補 Example |
| modify | `transactions/編輯收支紀錄.feature` | 同上 |

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|---|---|---|
| create | `POST /api/categories` | 新增分類 |
| create | `GET /api/categories` | 查詢分類列表 |
| modify | `TransactionInput` schema | `category: string` → `categoryId: integer` |
| modify | `Transaction` schema | `category: string` → `categoryId: integer`（前端比照 `accountId` 的模式，另外用 `GET /api/categories` 取名稱做本地 id→name 對應） |
| modify | `POST/PUT /api/transactions` | 新增 404「找不到該分類」錯誤分支 |

## Phase 05-07: Implementation

| 操作 | 目標 | 說明 |
|---|---|---|
| create | `category` model/repository/service/endpoint + migration + seed | 新表；migration 內建 17 筆預設分類 seed data |
| modify | `ledger_transaction` model/service | `category_id` FK、分類存在性檢查、CashPosition 同步邏輯不受影響（分類與 CashPosition 同步無關） |
| red-green-refactor | `categories/*.feature` + 修改過的 `transactions/*.feature` | 全部重跑 TDD |
| create | 前端分類選擇/新增元件 | 取代 `TransactionForm.tsx` 的自由文字 input，延續現有 Dark UI 風格 |
| modify | `TransactionForm.tsx`、MSW handlers/fixtures | `category` → `categoryId` |

## IMPL_IMPACT（由 Phase 02-04 Reconciler 回填）

| Phase | 影響目標 | Impact Type | 來源 | 說明 |
|---|---|---|---|---|
| 05 | `app/models/category.py`（新） | NEW_OPERATION | Phase 02 | 新表 |
| 05 | `app/models/ledger_transaction.py` | FIELD_CHANGE | Phase 02 | category:varchar → category_id:FK |
| 05 | `alembic/versions/` | FIELD_CHANGE + NEW_OPERATION | Phase 02 | 新 migration：建 category 表 + seed 17 筆 + 改 ledger_transaction.category_id |
| 05 | step_defs/transactions_steps.py | SENTENCE_PATTERN | Phase 03 | 新增分類存在性檢查的步驟資料解析 |
| 06 | `mocks/handlers/categories.ts`（新）、`mocks/fixtures.ts` | ENDPOINT_SCHEMA | Phase 04 | 新 endpoint mock |
| 06 | `lib/api/transactions.ts`、`lib/types/transaction.schema.ts` | ENDPOINT_SCHEMA | Phase 04 | category → categoryId |
| 06 | `components/TransactionForm.tsx` | ENDPOINT_SCHEMA | Phase 04 | 分類欄位改成選擇/新增元件 |
| 07 | — | — | auto | Phase 05 或 06 有影響 → 重跑整合驗證 |

## Phase 05 實作中發現的修正（追溯記錄）

**發現**：`TransferService` 用硬編碼字串 `category="轉帳"` 建立轉帳產生的兩筆紀錄，但 17 個預設分類中沒有「轉帳」（只有「轉帳手續費」），category 變成 FK 後會解析失敗。

**決定**（使用者選擇）：轉帳紀錄不需要分類。`ledger_transaction.category_id` 改為 nullable：一般收支紀錄由 service 層強制必填並驗證存在性，`is_transfer=true` 的轉帳紀錄則為 null（轉帳是資產搬移，非分類收支）。

**已回溯更新**：
- `specs/erm.dbml`：`category_id` 移除 DB 層 not null，改用 Note 說明由 service 層依 is_transfer 決定必填性
- `specs/api.yml`：`Transaction.categoryId` 加上 `nullable: true`（`TransactionInput.categoryId` 維持必填，因為轉帳走 `TransferInput`，不經過這個 schema）
