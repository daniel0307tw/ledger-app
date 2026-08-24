# Phase 07: Integration Validation ★

## 審查進度

- [x] 07.1 相關規格已審查 — **簽名**: 2026-08-24 22:15
- [x] 07.2 交付物已審查 — **簽名**: 2026-08-24 22:15

## 自我審查備註

**（2026-08-24 補跑）Chrome E2E 已完整執行**：環境當時沒有 Chrome，改設定 Playwright MCP 用 `--executable-path` 指向機器上已有的 Playwright 內建 Chromium（`~/.cache/ms-playwright/chromium-1234`）+ `--headless`（機器無 X 顯示伺服器），重新連線後即可正常啟動瀏覽器。對真實後端（`uvicorn app.main:app --port 8001`，手動啟動，非 systemd）+ 真實 PostgreSQL 資料庫（`ledger_app_dev`，真實使用者財務資料，62 筆既有交易）+ 真實前端 dev server（port 3001，`MOCK_API=false`）逐頁實測：

- `/settings`：4 個入口卡片 + 底部導覽 5 分頁，連結全數正確
- `/settings/recurring-transactions`：空狀態 → 建立規則（觸發自動生成 3 期真實交易）→ 補生成按鈕正確回報「目前不需要補生成」→ 刪除規則 → 回空狀態
- `/settings/budgets`：空狀態 → 建立分類預算與總預算 → 超支狀態正確計算（用真實既有交易金額驗證）→ 刪除 → 回空狀態
- `/settings/cloud-invoices`：空狀態 → 用直接 API 呼叫 `POST /cloud-invoices/sync`（Hermes-only 端點，非網頁操作）灌兩筆測試發票觸發 `pending_review` → 健康狀態卡片與待確認清單正確更新 → 「這是重複的」與「確認為新交易」兩個按鈕皆驗證 → 回空狀態

全程 console 監看 0 errors（僅 1 個既有、與本輪無關的 `apple-mobile-web-app-capable` deprecation warning）。所有測試建立的交易、規則、預算、雲端發票紀錄均已清理，測試後 curl 驗證 7 個帳戶餘額、62 筆交易數與測試前逐一比對一致。

**這一輪額外發現並修正 2 個真實 bug（延續 Phase 07 的既有精神：兩條 track 各自測試通過≠合在一起能跑，這次是「補跑 Chrome E2E」本身又揭露了新的整合問題）**：
1. **`/budgets/status` 回應完全沒有 `id` 欄位**：前端預算頁面 import 了 `deleteBudget` API 卻連 id 都拿不到，UI 上也真的沒有刪除按鈕——契約層（api.yml `BudgetStatus`）就沒定義這個欄位。修正 api.yml + 後端 `BudgetStatusOut`/`BudgetService.get_status()` + 前端 `BudgetStatusSchema`，並在 `budgets/page.tsx` 補上刪除按鈕。
2. **刪除操作沒有清除舊的錯誤訊息**：`recurring-transactions/page.tsx` 與 `budgets/page.tsx` 的 `handleDelete` 只在失敗時 `setError`，成功時沒有 `setError(null)`——實測時親眼看到刪除規則成功後，畫面還留著前一步「目前不需要補生成」的舊提示，容易誤導使用者以為刪除失敗或狀態異常。兩處都補上成功時清空 error。

**這個環境舊有的限制記錄（原文保留）**：以下為 2026-08-24 之前、Chrome 尚未裝好前的舊版驗證方式，改用對真實後端直接 API 呼叫，完整跑過驗證矩陣 5 項。

**套用 migration 到真實資料庫前先 `pg_dump` 備份**（`/tmp/.../scratchpad/ledger_app_dev_backup_before_migration_004.sql`），過程中發生的異動都已驗證可還原、且最終資料完整性確認無誤（62 筆交易、7 個帳戶前後一致）。

**這個 Phase 實際發現並修正 2 個真實 bug（正是 Integration Validation 這個 Phase 存在的意義——兩條 track 各自測試通過≠合在一起能跑）**：
1. **Migration 004 對已存在的 `transaction_type` enum 重複建立**：在全新資料庫一次跑完 001→004 時不會觸發（同一 connection 的記憶體 memo 蓋過去了），但對「已經在 003 的既有資料庫只補跑 004」（正是真實環境的實際情況）會直接炸掉。改用 `postgresql.ENUM(..., create_type=False)`（非 plain `sa.Enum`）解決。
2. **`cloud_invoice.transaction_id` FK 沒有 `ON DELETE` 行為**：實測「同步雲端發票建立交易 → 使用者事後手動刪除那筆交易」這個完全合法的操作流程時，被 FK 擋下丟出 Internal Server Error（前端只會看到不知所云的錯誤）。新增 migration 005，比照 `source_recurring_transaction_id` 的既有設計改成 `ON DELETE SET NULL`。

**驗證矩陣 5 項結果**：
1. Response envelope 格式 — 通過（所有回應均為 `{success, data}` / `{success, error:{message}}`）
2. 欄位名一致性 — 通過（前端 Zod schema camelCase 與後端回應逐一核對一致）
3. Auth flow — 不適用（既有系統無認證機制，本輪新 endpoint 沿用同一慣例，已於 Phase 01 查證）
4. Query params 完整性 — 通過（`/budgets/status` 依設計無參數，其餘 path/body 參數皆核對過）
5. Error handling — 通過（實測 404「找不到該預算」、422「總預算已存在」，並在測試過程中額外發現上述 bug 2）

所有測試資料（budget/recurring-transaction/cloud-invoice/transaction）均已清理，真實資料庫最終狀態與測試前一致。

## 目的 (What)

驗證前端（Phase 06）與後端（Phase 05）透過真實 HTTP 連線能正確協作。

**這不是「加一個檢查」— 這是正式的 Phase**，有完整的 2 步審查。

來源：從 CRM 專案 6 個整合問題中提煉的 architectural fix。
兩條獨立 track 各自通過測試 ≠ 合在一起能跑。

核心動作：前端關閉 MSW mock → rewrite proxy → 打真實後端 API。

**IMPL_IMPACT 感知**：若 Phase 05 或 Phase 06 有任何 Targeted Fix，Phase 07 自動觸發完整重驗（不可跳過）。Targeted Fix 改了前後端的局部，整合驗證確認局部修復沒有破壞全局。

**依賴**：Phase 05 + Phase 06 都必須在 `done/` 中。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | api.yml | Phase 04 | 契約 = 驗證基準 |
| 2 | Chrome Test Guard 測試計畫 | Phase 06 | 同一份測試計畫，換 real backend 重跑 |

## 交付物

carry-on Step 07.2 觸發時：

### 1. 啟動後端

```bash
# 方式 A: Docker
docker-compose up -d

# 方式 B: venv
source venv/bin/activate && uvicorn app.main:app --port 8000
```

健康檢查：`curl http://localhost:8000/health`

### 2. 前端環境切換

修改 `/home/daniel/dev/ledger-app/frontend/.env.development`：
```
NEXT_PUBLIC_MOCK_API=false
BACKEND_URL=http://localhost:8000
```

### 3. 驗證矩陣（5 項）

詳見 `references/integration-matrix.md`。

| # | 驗證項目 | 方法 |
|---|---------|------|
| 1 | Response envelope 格式 | 打 API → 檢查 `{success, data/error}` 結構 |
| 2 | 欄位名一致性 | 前端 type vs 後端 response vs api.yml |
| 3 | Auth flow | login → cookie → authenticated request |
| 4 | Query params 完整性 | 前端傳參 vs 後端接參 |
| 5 | Error handling | 觸發 4xx/5xx → 前端正確顯示 |

### 4. Chrome E2E 重跑

用 Chrome E2E 重跑 Phase 06 的 Chrome Test Guard 測試計畫（real backend mode）。

### 5. 問題修正迴圈

發現問題 → 定位（前端 / 後端 / 契約）→ 修正 → 重跑 → 直到全部通過。

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 07.1 | Chrome E2E 結果（real backend） | 4 頁全數以 Playwright + 真實後端/真實資料庫實測，見上方自我審查備註 | DONE（2026-08-24 補跑） |
| 07.2 | 驗證矩陣通過紀錄 | 5/5 全通過（見上方自我審查備註） | DONE |

### 驗收點

- [x] 後端啟動且健康檢查通過（真實後端 + 真實 PostgreSQL）
- [x] 前端 `MOCK_API=false` 且 rewrite proxy 正確（既有設定沿用，`web/.env.development` 未變動）
- [x] 驗證矩陣 5 項全部通過
- [x] Chrome E2E real 模式全數通過（2026-08-24 補跑，見上方自我審查備註；過程中額外發現並修正 2 個 bug）
