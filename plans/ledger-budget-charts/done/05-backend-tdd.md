# Phase 05: Backend TDD Track

## 審查進度

- [x] 05.1 相關規格已審查 — **簽名**: 2026-08-23 20:35
- [x] 05.2 交付物已審查 — **簽名**: 2026-08-23 20:35

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
| 05.1 | Step Definitions（新檔案） | `/home/daniel/dev/ledger-app/tests/features/steps/reports_steps.py` | DONE |
| 05.2 | Repository 方法（modify） | `/home/daniel/dev/ledger-app/app/repositories/transaction_repository.py`（新增 `sum_amount_by_category`） | DONE |
| 05.3 | Service（新檔案） | `/home/daniel/dev/ledger-app/app/services/report_service.py` | DONE |
| 05.4 | Schema（新檔案） | `/home/daniel/dev/ledger-app/app/schemas/report.py` | DONE |
| 05.5 | API Endpoint（新檔案 + 註冊） | `/home/daniel/dev/ledger-app/app/api/reports.py`、`app/api/__init__.py` | DONE |
| 05.6 | DB Migrations | 無需新增（Phase 02 確認 erm.dbml 無變動） | N/A |
| 05.7 | 回歸測試結果 | 全專案回歸測試全通過 | DONE |

### 實作紀錄

- 查詢邏輯：`TransactionRepository.sum_amount_by_category()` 對 `ledger_transaction JOIN category`，篩選 `type=支出 AND is_transfer=false AND date BETWEEN`，`GROUP BY category.name`，依金額降冪排序。
- 錯誤處理沿用既有機制：缺少 query 參數由 `app/main.py` 既有的 `RequestValidationError` 全域 handler 轉成 400「必要參數未提供」，不需新增程式碼；起訖顛倒由 `ReportService` 拋 `InvalidParameterError`，同一支既有的 400 handler 處理。
- **刻意不修改**既有共用 Then step `操作成功，查詢結果應包含：`，改為 `reports_steps.py` 新增獨立 Step Def，避免影響 transactions/accounts/categories 既有測試（與 Phase 03 的判斷一致）。
- **Red 階段發現一個框架層級的認知落差並修正**：原本 Feature 草稿用 `Given 使用者將帳戶轉帳：` 重用既有轉帳 Step Def 來製造轉帳前置紀錄，但實測後發現 Behave 的 `@given`/`@when`/`@then` 各自獨立註冊（`StepRegistry.find_step_definition` 只在對應 `step_type` 的清單裡找，不會跨關鍵字比對），該 Step Def 只註冊在 `@when`，用 `Given` 呼叫會是 undefined step。已將該行改為 `When`（句型文字不變，只換關鍵字），並同步修正 `reports/句型.md` 的說明。
- **順帶修正一個環境風險**：Phase 05 完成後重啟本機 uvicorn（daniel 手機日常使用的那個服務，port 8001）以載入新路由時，發現它先前的 `CASH_POSITION_DB_PATH` 環境變數殘留指向 ledger-category 輪 Phase 07 測試用的暫存檔案，而非真正的 `stock_analyzer.db`——這代表如果使用者這段期間用手機記帳，同步會寫進暫存檔案而非真正的現金部位追蹤表。已確認 Postgres `ledger_transaction` 在此期間為 0 筆（使用者未受影響），重啟時移除該環境變數覆寫，恢復指向真正的 `stock_analyzer.db`（config.py 的預設值）。

### 驗收點

- [x] 所有 .feature × 3 phase 任務 completed（Red 與 Green 合併執行，撰寫測試與實作後一次跑通，再走 Refactor 檢視）
- [x] 回歸測試全數通過（零失敗，連續 2 次確認非 flaky：10 features / 33 rules / 44 scenarios / 151 steps）
- [x] 真實 `stock_analyzer.db` 全程未受影響（cash_position 表維持 5 筆）
