# Phase 02: Entity Modeling（外部品質 — 資料）

## 審查進度

- [x] 02.1 相關規格已審查 — **簽名**: 2026-08-23 20:18
- [x] 02.2 交付物已審查 — **簽名**: 2026-08-23 20:18

## 目的 (What)

從 Phase 01 的 Feature Files（Rules）推導資料結構——系統操作「作用在什麼實體上」。

**erm.dbml 必須在 BDD Analysis 之前完成。** Phase 03 的 QA 五維分析需要知道欄位名、型別、約束條件才能推導精準的 Examples。

**Reconciler 模式**：entity-spec 以 desired-state reconciliation 運作——讀取現有 erm.dbml（若存在）→ 推導 desired state → 計算 diff → 增量更新。Greenfield 時 current = 空。讀取 Execution Plan 中 Phase 02 的 scope 決定工作範圍。

**依賴**：Phase 01 必須在 `done/` 中。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | Execution Plan | Phase 01 交付 | 本 Phase 的工作範圍（create/modify/delete 哪些實體） |
| 2 | Feature Files（Rules） | Phase 01 交付 | 行為規則——每個 command/query 操作的前置/後置條件 |
| 3 | Activity Diagrams | Phase 01 交付 | 流程結構——實體間的關聯與生命週期 |

## 交付物

carry-on Step 02.2 觸發時：

1. **DELEGATE `/aibdd-form-entity-spec`**，傳入：
   - Feature Files 路徑（`tests/features/`）
   - Activity Diagrams 路徑（`specs/activities/`）
   - 輸出路徑（`specs/erm.dbml`）
   - Execution Plan scope（Phase 02 區段）
2. entity-spec 以 Reconciler 6 步執行：Derive Desired → Read Current → Compute Diff → Preview → Apply with Clarify → Output
3. 產出 erm.dbml 後回傳控制權

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 02.1 | erm.dbml | `/home/daniel/dev/ledger-app/specs/erm.dbml`（無異動，reconcile diff = 空集） | DONE |
| 02.2 | 澄清紀錄 | 無 CiC，不適用 | N/A |

### Reconciler 執行紀錄

Execution Plan Phase 02 區段標示「無操作」。實際核對 `查詢分類花費統計.feature` 的資料需求（依 category_id 分組、SUM(amount)、篩選 type=支出 / is_transfer=false / date 區間）against 既有 `category`（id, name）與 `ledger_transaction`（category_id, amount, type, is_transfer, date）兩張表，所有欄位皆已存在，無需新增欄位或資料表。Diff = 空集，erm.dbml 維持原樣。

### 驗收點

- [x] erm.dbml 已產出（維持既有內容，確認無需變更）
- [x] Grep `CiC\(` 掃描 `specs/erm.dbml` 結果為空
- [x] 每個 Feature 中的操作都能追溯到 erm.dbml 中的實體（category + ledger_transaction 已足夠）
- [x] 欄位名、型別、約束條件完整（沿用既有定義）
