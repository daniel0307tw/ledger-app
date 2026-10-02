# Phase 02: Entity Modeling（外部品質 — 資料）

## 審查進度

- [x] 02.1 相關規格已審查 — **簽名**: 2026-09-16 20:55
- [x] 02.2 交付物已審查 — **簽名**: 2026-09-16 20:55

## 重新審查原因（2026-09-16）

Phase 03 分析途中發現：ledger-app 目前完全是單一幣別系統（`ledger_transaction` 無 currency 欄位，
`cash_sync.py` 寫死 `CURRENCY = "TWD"`），但第一輪已確認 stock_analyzer 會送實際幣別（美股交易可能
是 USD）。與使用者確認後決定：ledger-app 新增 `currency` 欄位開始支援多幣別。

**範圍澄清**：`is_stock_sync=true` 的交易已經是 `is_transfer=true`（不計入報表/預算），所以新增
`currency` 欄位**不需要**連動修改任何既有報表/預算查詢邏輯——那些查詢本就排除 is_transfer=true 的
交易。因此這不是「幫全系統加上多幣別支援」的大工程，只是讓這張表能夠**記錄**一個目前唯一會用到非
TWD 值的來源（stock_analyzer 的美股同步）欄位，既有的一般收支交易固定寫入 TWD，行為不變。

## Change Summary

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `ledger_transaction` table | +`is_stock_sync`:boolean (not null, default false) |
| modify | `ledger_transaction` table | +`currency`:varchar (not null, default 'TWD') |

## IMPL_IMPACT

| Impact Type | Phase | 影響目標 |
|-------------|-------|---------|
| FIELD_CHANGE | 05 | `app/models/ledger_transaction.py`（新增 2 欄位）+ Alembic migration（新增欄位，預設值 false/'TWD'，既有資料不受影響） |

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
   - Feature Files 路徑（`specs/features/`）
   - Activity Diagrams 路徑（`specs/activities/`）
   - 輸出路徑（`specs/entity/erm.dbml`）
   - Execution Plan scope（Phase 02 區段）
2. entity-spec 以 Reconciler 6 步執行：Derive Desired → Read Current → Compute Diff → Preview → Apply with Clarify → Output
3. 產出 erm.dbml 後回傳控制權

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 02.1 | erm.dbml | `specs/entity/erm.dbml` | PENDING |
| 02.2 | 澄清紀錄 | `specs/clarify/` | PENDING |

### 驗收點

- [ ] erm.dbml 已產出
- [ ] Grep `CiC\(` 掃描 `entity/erm.dbml` 結果為空
- [ ] 每個 Feature 中的操作都能追溯到 erm.dbml 中的實體
- [ ] 欄位名、型別、約束條件完整
