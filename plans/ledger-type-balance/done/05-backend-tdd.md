# Phase 05: Backend TDD Track

## 審查進度

- [x] 05.1 相關規格已審查 — **簽名**: 2026-08-23 22:10
- [x] 05.2 交付物已審查 — **簽名**: 2026-08-23 22:10

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

本輪為 **Targeted Fix** 模式（所有 IMPL_IMPACT 皆為 FIELD_CHANGE/DATATABLE_SCHEMA/SENTENCE_PATTERN/ENDPOINT_SCHEMA，無 NEW_OPERATION）。

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 05.1 | Step Definitions | `tests/features/steps/{shared_steps,categories_steps,accounts_steps,transactions_steps}.py` | DONE |
| 05.2 | Domain Models | `app/models/{category,account}.py`（+type enum） | DONE |
| 05.3 | Repositories | `app/repositories/{category_repository,account_repository,transaction_repository}.py` | DONE |
| 05.4 | Services | `app/services/{category_service,account_service,transaction_service}.py` | DONE |
| 05.5 | Schemas | `app/schemas/{category,account}.py` | DONE |
| 05.6 | API Endpoints | `app/api/{categories,accounts}.py` | DONE |
| 05.7 | Seed Data | `app/core/seed_data.py`（17→20 筆，含 type） | DONE |
| 05.8 | DB Migration | `alembic/versions/003_add_category_and_account_type.py` | DONE |
| 05.9 | 回歸測試結果 | 全數通過，連續兩次執行皆穩定 | DONE |

### 實作重點

- `category.type` / `account.type` 皆為 NOT NULL enum 欄位（`CategoryType`/`AccountType`，`str, enum.Enum` 慣例比照既有 `TransactionType`）
- `TransactionService.create_transaction`/`update_transaction` 新增 `_assert_category_type_matches`：分類 type=皆可 時放行，否則須與交易 type 完全相符，違反時 `raise BusinessError("分類收支類型與交易類型不符")` → 422（比照既有 `transfer_service.py` 的 SAME_ACCOUNT 422 慣例）
- `AccountService.list_accounts`/`create_account` 改回傳 dict（非 ORM 物件）以夾帶計算出的 `balance`；`TransactionRepository.sum_balance_by_account()` 用 SQL `CASE WHEN type=收入 THEN amount ELSE -amount END` 全域加總（含轉帳紀錄），group by account_id，一次查詢涵蓋所有帳戶
- Migration 003：以 blanket `UPDATE account SET type='一般帳戶'`（不寫死帳戶名稱清單）+ `UPDATE category SET type=...`（依名稱是否為「校正回歸」二分）+ `bulk_insert` 3 筆新收入分類，欄位先允許 nullable backfill 完再 `alter_column` 為 NOT NULL

### 自我審查中發現並修正的問題

1. **既有回歸測試中的資料錯誤**：`新增收支紀錄.feature` 的 CashPosition 同步 Scenario Outline 原本兩個案例都寫死用「餐飲」（支出類）分類，新增的分類類型驗證會讓「收入」案例失敗——已在 Phase 03 修正為新增 category 欄位、收入案例改用「薪資」。
2. **共用 Then step 需擴充**：`transactions_steps.py` 的 `操作成功，查詢結果應包含：` 這個 Then 被 categories/accounts/transactions 三個 domain 共用，原本 else 分支只比對 name；擴充為依 headings 是否含 `balance`/`type` 判斷該用哪種 tuple 集合比對，向後相容既有分支。
3. **`Given 系統中有以下收支紀錄：` 缺少 id 欄位會噴例外**：新增到 `accounts/查詢帳戶列表.feature` 的兩個 Example 一開始漏了 `id` 欄位（該 step 的既有實作要求必填），跑測試立即發現並修正。

### 部署驗證（真實環境，非測試容器）

- 對真實 Postgres DB（`ledger_app_dev`，即時運行中的 backend 所連接的資料庫）執行 `alembic upgrade head`：驗證 20 筆分類、5 筆帳戶（含原先未列在 Discovery 假設中的「現金」帳戶，blanket UPDATE 設計因此仍正確涵蓋）皆正確回填 type
- 重啟即時 uvicorn process（PID 2198793 → 新 PID），`/health`、`/api/accounts`、`/api/categories` 皆回應正確，含新欄位
- 確認重啟後的 process 無 `CASH_POSITION_DB_PATH` 覆寫（沿用 `app/core/config.py` 真實預設路徑），且 `stock_analyzer.db` 的 `cash_position` 表列數在整個過程中維持 5 筆不變

### 驗收點

- [x] 所有受影響 .feature 的 Targeted Fix 完成
- [x] 回歸測試全數通過（10 features / 36 rules / 50 scenarios / 170 steps），連續執行兩次皆零失敗、零 flaky
- [x] 真實資料庫 migration 已套用且驗證正確
- [x] 即時 backend process 已重啟並驗證健康
- [x] stock_analyzer.db 安全不變式全程保持（cash_position 列數 = 5）
