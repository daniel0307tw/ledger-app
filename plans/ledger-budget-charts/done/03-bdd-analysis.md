# Phase 03: BDD Analysis（外部品質 — 可執行規格）

## 審查進度

- [x] 03.1 相關規格已審查 — **簽名**: 2026-08-23 20:25
- [x] 03.2 交付物已審查 — **簽名**: 2026-08-23 20:25

## 目的 (What)

從已確認的 Feature Rules（Phase 01）+ 實體結構（Phase 02）推導最小必要句型集，
填入具體 Examples，將 Feature Files 從「行為骨架」升級為「可執行規格」。

**三階段推導**：系統抽象 → 句型模型 → Feature with Examples。
每個階段都需使用者審核才能進入下一個。

**Reconciler 模式**：bdd-analysis 以三層 desired-state reconciliation 運作——每層各自 derive desired → read current → compute diff → preview → apply。讀取 Execution Plan 中 Phase 03 的 scope 決定哪些 domain 需分析。

**Boundary 偵測**：若偵測到 erm.dbml（Phase 02 已完成），
載入 web-backend preset（句型分析方針 + Handler 決策樹）。

觸發 skill：`/aibdd-form-bdd-analysis`

**依賴**：Phase 02 必須在 `done/` 中。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | Execution Plan | Phase 01 交付 | 本 Phase 的工作範圍（哪些 domain 需分析） |
| 2 | Feature Files（Rules） | Phase 01 交付 | CiC 歸零的行為骨架 |
| 3 | erm.dbml | Phase 02 交付 | 實體結構——欄位、型別、約束 |

## 交付物

carry-on Step 03.2 觸發時：

1. **DELEGATE `/aibdd-form-bdd-analysis`**，傳入：
   - features 資料夾路徑（`tests/features/`）
   - 澄清紀錄路徑（`specs/clarify/`）
   - Execution Plan scope（Phase 03 區段）
2. bdd-analysis 以 Reconciler 模式依序執行三階段（每層各自 reconcile）：
   - **系統抽象推導** → 展示並等待使用者審核
   - **各 domain 句型模型推導** → 展示並等待使用者審核
   - **產出 Feature Files（填入 Examples）** → 展示摘要並等待使用者審核
3. 完成後回傳控制權

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 03.1 | 系統抽象（modify，+1 操作列） | `/home/daniel/dev/ledger-app/tests/features/系統抽象.md` | DONE |
| 03.2 | 句型模型（create） | `/home/daniel/dev/ledger-app/tests/features/reports/句型.md` | DONE |
| 03.3 | Feature Files（含 Examples） | `/home/daniel/dev/ledger-app/tests/features/reports/查詢分類花費統計.feature` | DONE |

### IMPL_IMPACT（回填至 execution-plan.md，供 Phase 05 參考）

| Phase | 影響目標 | Impact Type | 說明 |
|-------|---------|-------------|------|
| 05 | `tests/features/steps/reports_steps.py`（新檔案） | NEW_OPERATION | 新 When「使用者查詢分類花費統計，起始日期...結束日期...」+ 新 Then「操作成功，查詢結果應包含以下分類花費統計：」需要全新 Step Def |
| 05 | `tests/features/steps/transactions_steps.py` | 無需修改 | 刻意不擴充既有共用 Then step `操作成功，查詢結果應包含：`（該 step 目前只支援「date 欄位」或「純 name 欄位」兩種資料形狀，不支援本 domain 的 category+total_amount 聚合形狀），改走獨立新句型以避免影響 transactions/accounts/categories 三個既有 domain 的既有測試 |

### 驗收點

- [x] `tests/features/系統抽象.md` 產出並經使用者審核
- [x] `tests/features/reports/句型.md` 產出並經使用者審核
- [x] `查詢分類花費統計.feature` 填入具體 Examples（7 個情境：2 條缺參數、1 條起訖顛倒、3 條分組加總含轉帳/收入排除、1 條無花費分類排除、1 條空結果）
- [x] `.feature` 已移除 `@ignore` tag（保留 `@query`）
- [x] QA 五維分析完整（見句型.md「測試分析」章節）
