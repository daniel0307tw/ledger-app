# Phase 05: Backend TDD Track

## 審查進度

- [ ] 05.1 相關規格已審查 — **簽名**: ___
- [ ] 05.2 交付物已審查 — **簽名**: ___

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
| 05.1 | Step Definitions | `/home/daniel/dev/ledger-app/features/steps/` | PENDING |
| 05.2 | Domain Models | `/home/daniel/dev/ledger-app/app/models/` | PENDING |
| 05.3 | API Endpoints | `/home/daniel/dev/ledger-app/app/api/` | PENDING |
| 05.4 | DB Migrations | `/home/daniel/dev/ledger-app/alembic/versions/` | PENDING |
| 05.5 | 回歸測試結果 | 回歸測試全通過 | PENDING |

### 驗收點

- [ ] 所有 .feature × 3 phase 任務 completed
- [ ] 回歸測試全數通過（零失敗）

---
## 產出（由背景 agent 實作，已獨立重跑驗證）
- app/repositories/transaction_repository.py：新增 find_by_category_in_range()
- app/services/report_service.py：新增 get_category_detail()
- app/api/reports.py：新增 GET /reports/category-detail
- tests/features/steps/reports_steps.py：新增 W2/T3 Step Def
- tests/features/steps/transactions_steps.py：擴充 step_given_transactions 支援 note 欄位（向下相容）

獨立重跑 .venv/bin/behave tests/features/ --tags=~@ignore：28 features / 126 scenarios / 468 steps 全綠，0 failed，與 agent 回報一致。locked contracts（api.yml/erm.dbml/feature Examples）未被更動。

## 簽核
LGTM: 2026-08-24 (標準授權自動推進，獨立驗證通過)
