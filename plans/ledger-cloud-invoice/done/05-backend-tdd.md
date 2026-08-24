# Phase 05: Backend TDD Track

## 審查進度

- [x] 05.1 相關規格已審查 — **簽名**: 2026-08-24 18:40
- [x] 05.2 交付物已審查 — **簽名**: 2026-08-24 18:40

## 自我審查備註

新增：3 個 model（cloud_invoice/recurring_transaction/budget）+ 1 個實作層級追加的 cloud_invoice_sync_error 表（記錄批次同步中資料錯誤筆數，供健康狀態查詢，Phase 02 未預先規劃，屬 Phase 05 發現的必要細節）+ 1 個 alembic migration（004）+ 3 個 repository + 3 個 service + 3 個 schema 檔 + 3 個 API router（10 個 endpoint）+ 3 個 step def 檔（14 個 feature、33 個 scenario）。

**過程中修正的真實 bug（實測發現，非憑空猜測）**：
1. Migration 004 最初對 4 個新 enum 型別先手動 `.create(checkfirst=True)`、又在 `create_table()` 用同一個 Enum 物件，導致 SQLAlchemy 在編譯 CREATE TABLE DDL 時重複建立型別（"type already exists"）——移除手動預建，交給 create_table 自動處理。
2. `ledger_transaction.source_recurring_transaction_id` 的 FK 一開始沒有 `ondelete=SET NULL`，導致刪除固定收支規則時被外鍵擋下（違反「已生成交易應保留」的 Rule）——加上 SET NULL。
3. 我自己在多個新 Feature 的 Background 誤加了「系統中有以下分類：」，跟 environment.py 每個 scenario 自動 seed 的 20 筆預設分類撞名（category.name 不強制唯一），導致 `find_by_name` 查詢 MultipleResultsFound——移除 12 個檔案裡誤加的分類宣告；同時把 `AccountRepository`/`CategoryRepository` 的 `find_by_name` 從 `.one_or_none()` 改成 `.first()`（依 id 排序），避免未來使用者真的建了同名分類/帳戶時查詢直接炸掉。
4. 「應建立一筆支出交易」共用 Then step 沒處理批次同步（list）與單筆確認（dict）兩種回應形狀，AttributeError——已修正為依型別分流。

**Refactor**：移除一個重複定義（`RecurringTransactionRepository.count_generated_transactions` 與 `TransactionRepository.count_by_source_recurring_transaction` 功能重複，服務層只用到後者，刪除前者）；把兩處函式內 `import TransactionType` 提到模組頂層；補上遺漏的回傳型別註記。

全專案回歸測試：25 features / 91 scenarios / 329 steps 全數通過，零破壞既有功能。

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
| 05.1 | Step Definitions（3 個新檔） | `tests/features/steps/{cloud_invoices,recurring_transactions,budgets}_steps.py` | DONE |
| 05.2 | Domain Models（4 個新檔 + 1 個修改） | `app/models/{cloud_invoice,cloud_invoice_sync_error,recurring_transaction,budget}.py` + `ledger_transaction.py` | DONE |
| 05.3 | API Endpoints（3 個新檔） | `app/api/{cloud_invoices,recurring_transactions,budgets}.py` | DONE |
| 05.4 | DB Migrations | `alembic/versions/004_add_cloud_invoice_recurring_budget.py` | DONE |
| 05.5 | 回歸測試結果 | 25 features / 91 scenarios / 329 steps 全通過 | DONE |

### 驗收點

- [x] 所有 .feature × 3 phase 任務 completed（14 個新 feature，33 個新 scenario）
- [x] 回歸測試全數通過（零失敗，含 24 個既有 feature）
