# Phase 03: BDD Analysis（外部品質 — 可執行規格）

## 審查進度

- [x] 03.1 相關規格已審查 — **簽名**: 2026-08-24 20:35
- [x] 03.2 交付物已審查 — **簽名**: 2026-08-24 20:35

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
   - features 資料夾路徑（`specs/features/`）
   - 澄清紀錄路徑（`specs/clarify/`）
   - Execution Plan scope（Phase 03 區段）
2. bdd-analysis 以 Reconciler 模式依序執行三階段（每層各自 reconcile）：
   - **系統抽象推導** → 展示並等待使用者審核
   - **各 domain 句型模型推導** → 展示並等待使用者審核
   - **產出 Feature Files（填入 Examples）** → 展示摘要並等待使用者審核
3. 完成後回傳控制權

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 03.1 | 系統抽象 | `/home/daniel/dev/ledger-app/tests/features/系統抽象.md`（modify） | DONE |
| 03.2 | 句型模型 | `/home/daniel/dev/ledger-app/tests/features/transactions/句型.md`（modify；budgets/reports 沿用既有句型模式，未新增句型類別，未修改各自句型.md） | DONE |
| 03.3 | Feature Files（含 Examples） | 見 Phase 01 卡片列出的 7 檔 | DONE |

驗證：`.venv/bin/behave --dry-run` 對 7 檔跑過，Gherkin 語法全數解析成功、無 ParserError，新句型正確列為 undefined steps（待 Phase 05 補 Step Def，符合預期，非錯誤）。

### 驗收點

- [x] `tests/features/系統抽象.md` 產出並更新
- [x] transactions domain 的 `句型.md` 產出並更新
- [x] 所有 .feature 填入具體 Examples
- [x] 所有 .feature 移除 `@ignore` tag（grep 確認為空）
- [x] QA 五維分析完整（等價類/邊界值/狀態轉移/組合覆蓋/錯誤推測，每個新 Rule 皆有對應 Example）
