# Execution Plan：ledger-budget-charts

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 5（1 Activity、1 Feature domain、1 API endpoint、1 前端頁面、1 底部導覽項目） |
| Modify | 1（BottomNav 新增第三分頁） |
| Delete | 0 |

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| 無操作 | — | 本輪為純查詢統計，不新增資料表欄位，erm.dbml 不需異動（`category` + `ledger_transaction` 既有結構已足夠支撐 GROUP BY 統計） |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `reports/` domain | 全新 domain，1 個 Query Feature：依分類查詢某月支出統計 |

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `GET /api/reports/category-summary`（endpoint 命名於 Phase 04 依 Feature 的 When 子句推導，此處為暫定） | 查詢某月依分類分組的支出統計，query param 為月份 |

## Phase 05: Backend TDD

| 操作 | 目標 | 說明 |
|------|------|------|
| red-green-refactor | `reports/*.feature` | 新 Query endpoint 的完整 TDD 循環 |

## Phase 06: Frontend Build

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `/reports` 頁面 | 新頁面：月份切換 + 圓餅圖（依分類佔比），沿用行事曆頁月份切換邏輯與既有 Dark UI 風格 |
| modify | `web/src/components/BottomNav.tsx` | 新增第三個 tab「報表」 |
| create | MSW handler + fixtures | 對應新 endpoint |

## Phase 07: Integration Validation

| 操作 | 目標 | 說明 |
|------|------|------|
| 全項驗證 | 新 query endpoint + 報表頁面 | 比照既有 Phase 07 驗證矩陣，含手機 viewport 截圖驗證（本輪新規則，圖表視覺需在窄螢幕確認無破版/過度擁擠） |

## IMPL_IMPACT（Phase 03 回填）

| Phase | 影響目標 | Impact Type | 說明 |
|-------|---------|-------------|------|
| 05 | `tests/features/steps/reports_steps.py`（新檔案） | NEW_OPERATION | 新 When + 新 Then 需要全新 Step Def，不擴充既有共用 query-result Then step（避免影響 transactions/accounts/categories 既有測試） |

## Rule 清單（供 Phase 03 BDD Analysis 直接引用，已於 Discovery Step 2 confirm）

- R1：`is_transfer=true` 的轉帳紀錄不計入統計
- R2：統計範圍僅 `type=支出` 的交易，不含收入
- R3：該月完全沒有花費的分類不出現在統計結果中
- R4：該月完全沒有支出紀錄時，回傳空結果（前端顯示空狀態，非圖表本身的 Rule，留給 Phase 06 落實 UI）
