# Execution Plan：ledger-type-balance

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 0 |
| Modify | 10（2 entity、6 feature、2 api endpoint 群組） |
| Delete | 0 |

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `category` table | +`type` 欄位，enum(收入/支出/皆可) |
| modify | `account` table | +`type` 欄位，enum(一般帳戶/信用卡) |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `categories/建立分類.feature` | Rule 新增：type 為必要參數；新分類的 type 沿用當下記帳表單的收支類型（前端決定送出值，後端只驗證有提供） |
| modify | `categories/查詢分類列表.feature` | Then 回應新增 type 欄位；Examples 補上 4 個新增分類（薪資/獎金/投資=收入、校正回歸=皆可） |
| modify | `accounts/建立帳戶.feature` | Rule 新增：type 為必要參數 |
| modify | `accounts/查詢帳戶列表.feature` | Then 回應新增 type + balance 欄位 |
| modify | `transactions/新增收支紀錄.feature` | Rule 新增：分類的收支類型必須符合交易類型（或分類為「皆可」），否則操作失敗（ASM，理由見下） |
| modify | `transactions/編輯收支紀錄.feature` | 同上 Rule 延伸至編輯 |

**ASM（Discovery 階段推論，Phase 03 會實際展示給使用者確認）**：分類-交易類型比對這條規則使用者原話沒有明說要在後端強制驗證，但這個專案既有的 CATEGORY_NOT_FOUND、ACCOUNT_NOT_FOUND 等驗證規則都是在 service 層強制執行、不只是前端 UI 過濾，比照既有慣例延伸此規則到後端，避免繞過前端直接呼叫 API 造成資料不一致（例如用支出分類的 id 建立一筆收入交易）。

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `POST/GET /api/categories` | Request/Response schema +type |
| modify | `POST/GET /api/accounts` | Request schema +type；Response schema +type +balance |
| modify | `POST/PUT /api/transactions` | 新增錯誤分支：分類類型不符 |

## Phase 05: Backend TDD

| 操作 | 目標 | 說明 |
|------|------|------|
| targeted-fix | category/account model + migration | +type 欄位、既有資料回填（17 分類→支出、4 帳戶→一般帳戶）、seed 4 個新分類 |
| targeted-fix | transaction service | 新增分類類型比對驗證 |
| targeted-fix | account service/repository | 餘額計算查詢（SUM 收入 - SUM 支出，依帳戶分組） |

## Phase 06: Frontend Build

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `CategoryPicker.tsx` | 接受 transactionType prop，依 type 過濾分類清單（皆可 兩邊都顯示）；內嵌新增分類時自動帶入當下 type |
| modify | `TransactionForm.tsx` | 切換收入/支出時，若已選分類不再有效則清空；傳遞 type 給 CategoryPicker |
| modify | 建立帳戶頁面/表單 | 新增帳戶類型選擇 |
| modify | 帳戶列表頁面 | 顯示每個帳戶的餘額/未繳金額 |

## Phase 07: Integration Validation

全項驗證比照既有慣例，含手機 viewport 截圖驗證。

## IMPL_IMPACT（Phase 02-04 完成後回填）

| Phase | 影響目標 | Impact Type | 來源 | 說明 |
|-------|---------|-------------|------|------|
| 05 | category model + migration | FIELD_CHANGE | Phase 02 | +type 欄位，既有 17 筆 seed 資料回填 type=支出，seed 新增 3 筆 type=收入（薪資/獎金/投資）+ 校正回歸改為 type=皆可 |
| 05 | account model + migration | FIELD_CHANGE | Phase 02 | +type 欄位，既有 4 筆帳戶回填 type=一般帳戶 |
| 05 | step_defs/shared_steps（系統中有以下帳戶） | DATATABLE_SCHEMA | Phase 03 | Given datatable +type column，未指定時預設 一般帳戶（保持既有無 type 欄位的 Background 相容） |
| 05 | step_defs/categories_steps | DATATABLE_SCHEMA + SENTENCE_PATTERN | Phase 03 | 建立分類/查詢分類列表 的 When/Then datatable +type column |
| 05 | step_defs/accounts_steps | DATATABLE_SCHEMA + SENTENCE_PATTERN | Phase 03 | 建立帳戶 的 When datatable +type；查詢帳戶列表 的 Then datatable +type +balance，需新增餘額計算查詢邏輯 |
| 05 | transaction_service | SENTENCE_PATTERN（新驗證分支） | Phase 03 | 新增/編輯收支紀錄新增 CATEGORY_TYPE_MISMATCH 業務規則驗證（422，比照既有 BusinessError 慣例） |
| 05 | app/api/transactions.py | ENDPOINT_SCHEMA | Phase 04 | POST/PUT /api/transactions 回應新增 422 分支 |
| 05 | app/api/accounts.py, category.py | ENDPOINT_SCHEMA | Phase 04 | Request/Response schema +type（accounts 另 +balance） |
| 06 | mocks/handlers/categories, accounts | ENDPOINT_SCHEMA | Phase 04 | Zod schema + MSW handler 反映 +type（accounts +balance） |
| 06 | CategoryPicker.tsx | FIELD_CHANGE | Phase 02/03 | 接受 transactionType prop 依 type 過濾；內嵌新增分類自動帶入當下 type |
| 06 | TransactionForm.tsx | SENTENCE_PATTERN | Phase 03 | 切換收入/支出時，若已選分類不再有效則清空；新增分類類型不符時的 422 錯誤顯示 |
| 06 | 建立帳戶表單 | FIELD_CHANGE | Phase 02/04 | 新增帳戶類型選擇欄位 |
| 06 | 帳戶列表頁面 | FIELD_CHANGE | Phase 02/04 | 顯示每個帳戶的 balance（一般帳戶標籤「餘額」，信用卡標籤「未繳金額」） |
| 07 | Integration Validation | — | auto | Phase 05 + 06 皆有變更 → 全項整合驗證，含手機 viewport 截圖驗證；Activity 結構本輪無變更，測試計畫沿用既有結構，僅涵蓋新增的驗證分支與欄位 |
