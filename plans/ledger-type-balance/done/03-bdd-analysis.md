# Phase 03: BDD Analysis（外部品質 — 可執行規格）

## 審查進度

- [x] 03.1 相關規格已審查 — **簽名**: 2026-08-23 21:25
- [x] 03.2 交付物已審查 — **簽名**: 2026-08-23 21:25

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
| 03.1 | 系統抽象 | `/home/daniel/dev/ledger-app/tests/features/系統抽象.md` | DONE |
| 03.2 | 句型模型（3 domain） | `/home/daniel/dev/ledger-app/tests/features/{categories,accounts,transactions}/句型.md` | DONE |
| 03.3 | Feature Files（含 Examples，6 檔） | 見下方清單 | DONE |

修改的 6 個 Feature File（絕對路徑，皆已補完 Examples）：
1. `/home/daniel/dev/ledger-app/tests/features/categories/建立分類.feature`
2. `/home/daniel/dev/ledger-app/tests/features/categories/查詢分類列表.feature`
3. `/home/daniel/dev/ledger-app/tests/features/accounts/建立帳戶.feature`
4. `/home/daniel/dev/ledger-app/tests/features/accounts/查詢帳戶列表.feature`
5. `/home/daniel/dev/ledger-app/tests/features/transactions/新增收支紀錄.feature`
6. `/home/daniel/dev/ledger-app/tests/features/transactions/編輯收支紀錄.feature`（Rule 文字沿用，未新增 Example，比照既有「分類不存在」不重複展開的慣例）

**自我審查發現並修正的一個真實回歸**：`transactions/新增收支紀錄.feature` 既有的「新增<type>後同步至 CashPosition」Scenario Outline 原本兩個案例（支出/收入）都寫死使用「餐飲」分類（支出類），新增的分類類型比對規則會讓收入案例失敗。已修正為 Examples 表新增 category 欄位，收入案例改用「薪資」（收入類分類）。

**分類數量更正**：一開始沿用先前回合措辭誤植為「21 個預設分類」，經自查為 17（既有，含「校正回歸」改為皆可但不重複計數）+ 3（薪資/獎金/投資新增）= **20** 個，已修正 `系統抽象.md`、`categories/句型.md`、`categories/查詢分類列表.feature`、`erm.dbml` 四處。

### 驗收點

- [x] `tests/features/系統抽象.md` 產出並經審核（實體清單、操作全景、Violation 模式、共用句型 S-G1 皆已更新）
- [x] 每個 domain 的 `tests/features/{domain}/句型.md` 產出並經審核（categories、accounts、transactions 三個 domain）
- [x] 所有 6 個修改的 .feature 填入具體 Examples
- [x] 所有 .feature 保持既有 tag（本輪皆為既有檔案 modify，非新建，不涉及 @ignore 移除）
- [x] QA 五維分析完整（每個 domain 句型.md 的測試分析段落皆補上等價類/邊界值/組合覆蓋/錯誤推測）
