# Phase 05: Backend TDD Track

## 審查進度

- [x] 05.1 相關規格已審查 — **簽名**: 2026-09-16 22:10
- [x] 05.2 交付物已審查 — **簽名**: 2026-09-16 22:10

## 完成摘要

**新增檔案**：
- `alembic/versions/007_add_stock_sync_to_ledger_transaction.py`
- `app/services/stock_sync_service.py`（獨立 service，不呼叫 sync_to_cash_position/cancel_previous_sync）
- `app/schemas/stock_sync.py`
- `app/api/stock_sync.py`
- `tests/features/steps/cash_sync_steps.py`

**修改檔案**：
- `app/models/ledger_transaction.py`（+is_stock_sync, +currency）
- `app/repositories/transaction_repository.py`（create() 新增兩個參數）
- `app/api/__init__.py`（註冊新 router）

**測試結果**：cash-sync 3 個 feature、7 條 Rule、10 個 Scenario、44 個 step 全數通過；
完整回歸測試（32 features、143 scenarios、547 steps）0 failed，無破壞既有功能。
black/isort 格式化通過，mypy 新增的錯誤與既有程式碼同類型（既有慣例，非本次引入的新問題）。

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
