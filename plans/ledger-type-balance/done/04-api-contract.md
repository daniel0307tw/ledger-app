# Phase 04: API Contract（內部品質）

## 審查進度

- [x] 04.1 相關規格已審查 — **簽名**: 2026-08-23 21:35
- [x] 04.2 交付物已審查 — **簽名**: 2026-08-23 21:35

## 目的 (What)

從已完成的 Feature Files 推導 API 契約。

**每個 command/query 天然對應一個 API endpoint** — 這是從行為規格直接推導的映射，不是獨立設計決策。

推導邏輯：
- Feature 中的 `When 使用者建立...`（command）→ `POST /api/...`
- Feature 中的 `When 使用者查詢...`（query）→ `GET /api/...`
- Request/Response 結構從 Feature 的 Data Table + erm.dbml 推導

**Reconciler 模式**：api-spec 以 desired-state reconciliation 運作——讀取現有 api.yml（若存在）→ 推導 desired state → 計算 diff → 增量更新。讀取 Execution Plan 中 Phase 04 的 scope 決定工作範圍。

觸發 skill：`/aibdd-form-api-spec`

**依賴**：Phase 03 必須在 `done/` 中。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | Execution Plan | Phase 01 交付 | 本 Phase 的工作範圍（create/modify/delete 哪些 endpoint） |
| 2 | Feature Files（含 Examples） | Phase 03 交付 | 完整的行為規格（command/query 分類已明確） |
| 3 | erm.dbml | Phase 02 交付 | 實體結構（推導 Request/Response schema） |

## 交付物

carry-on Step 04.2 觸發時：

1. **DELEGATE `/aibdd-form-api-spec`**，傳入：
   - Feature Files 路徑（`tests/features/`）
   - erm.dbml 路徑（`specs/erm.dbml`）
   - 輸出路徑（`specs/api.yml`）
   - Execution Plan scope（Phase 04 區段）
2. api-spec 以 Reconciler 6 步執行：Derive Desired → Read Current → Compute Diff → Preview → Apply with Clarify → Output
3. 產出 api.yml 後回傳控制權

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 04.1 | api.yml | `/home/daniel/dev/ledger-app/specs/api.yml` | DONE |
| 04.2 | 澄清紀錄 | 無新便條紙；422 狀態碼決策依據既有 exceptions.py 的 BusinessError 慣例（見下方修改摘要），非新判斷 | DONE |

修改摘要：
- 新增 Enum `CategoryType { 收入, 支出, 皆可 }`、`AccountType { 一般帳戶, 信用卡 }`
- `CategoryInput`/`Category` schema +`type`（必要欄位）
- `AccountInput`/`Account` schema +`type`（必要欄位）、`Account` +`balance`（必要欄位）
- `POST /api/transactions`、`PUT /api/transactions/{id}` 回應新增 `422` 分支（對應 CATEGORY_TYPE_MISMATCH，比照 app/exceptions.py 既有的 `BusinessError`→422 慣例，與既有 `/api/transfers` 的 SAME_ACCOUNT 422 一致）

驗證：`python3 -c "import yaml; yaml.safe_load(open('specs/api.yml'))"` 通過，YAML 可解析。

### 驗收點

- [x] api.yml 已產出
- [x] Grep `CiC\(` 掃描 `specs/api.yml` 結果為空
- [x] 每個 Feature 的 command/query 都有對應的 API endpoint（本輪為既有 endpoint 的 schema modify，路徑不變）
- [x] Request/Response schema 與 erm.dbml 欄位一致
- [x] Response envelope 格式統一（`{ success, data/error }`）
