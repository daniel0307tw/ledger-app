# Phase 03: BDD Analysis（外部品質 — 可執行規格）

## 審查進度

- [x] 03.1 相關規格已審查 — **簽名**: 2026-08-24 15:40
- [x] 03.2 交付物已審查 — **簽名**: 2026-08-24 15:40

## 自我審查備註

3 個新 domain（cloud-invoices/recurring-transactions/budgets）共 14 個 Feature 全部補上 Examples（共 27 個 Scenario）。系統抽象.md 已更新（3 個新實體、14 個新操作、7 個新 violation、5 個新變異點）。過程中修正一處句型誤用（編輯規則的 Then 誤沿用刪除規則的句型文字，已改為獨立的 T4b）。驗收檢查：@ignore 標籤、Example 佔位標記、CiC 便條紙三項掃描均為 0。

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
| 03.1 | 系統抽象 | `tests/features/系統抽象.md` | DONE |
| 03.2 | 句型模型 | `tests/features/{cloud-invoices,recurring-transactions,budgets}/句型.md` | DONE |
| 03.3 | Feature Files（含 Examples，14 個） | `tests/features/{cloud-invoices,recurring-transactions,budgets}/*.feature` | DONE |

### 驗收點

- [x] `features/系統抽象.md` 產出（自我審核，go until need clarify 模式）
- [x] 每個 domain 的 `features/{domain}/句型.md` 產出
- [x] 所有 .feature 填入具體 Examples
- [x] 所有 .feature 移除 `@ignore` tag
- [x] QA 五維分析完整（每個操作至少涵蓋等價類，關鍵操作另涵蓋邊界值/組合覆蓋/錯誤推測）
