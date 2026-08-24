# Phase 07: Integration Validation ★

## 審查進度

- [x] 07.1 相關規格已審查 — **簽名**: 2026-08-23 20:39
- [x] 07.2 交付物已審查 — **簽名**: 2026-08-23 20:39

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

修改 `/home/daniel/dev/ledger-app/web/.env.development`：
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
| 07.1 | Chrome E2E 結果（real backend） | 全通過 | DONE |
| 07.2 | 驗證矩陣通過紀錄 | 4/4 通過 + 1 項 N/A | DONE |

### 驗證矩陣紀錄

| # | 項目 | 結果 |
|---|------|------|
| 1 | Response envelope | PASS — `{success, data}` / `{success, error:{message}}` 一致 |
| 2 | 欄位名一致性 | PASS — `categoryId`/`totalAmount` 等前端 type、後端 response、api.yml 三方一致 |
| 3 | Auth flow | N/A — 本專案單人使用無 auth 機制（沿用 ledger-category 輪的既有結論） |
| 4 | Query params | PASS — 缺 startDate/endDate → 400「必要參數未提供」；起訖顛倒 → 400「起始日期不可晚於結束日期」 |
| 5 | Error handling | PASS（過程中發現並修正一個真實 bug，見下） |

### 實作中發現並修正的問題

**`web/src/lib/api/client.ts` 的錯誤處理有真實缺口**：後端無法連線時，Next.js rewrite proxy 回傳的不是 JSON（例如純文字的 Internal Server Error），但 `apiClient` 直接對回應內容做 `res.json()` 沒有防呆，丟出瀏覽器原生的 JSON parse 例外（例如「Unexpected token 'I', "Internal S"... is not valid JSON」），這段訊息會直接被頁面的 `catch` 顯示給使用者看，體驗很差。這是共用程式碼，所有頁面都會受影響，不只是本輪新增的報表頁。用 Playwright 手動關掉後端、載入 `/reports` 頁面時發現。

修法：`res.json()` 包一層 try/catch，解析失敗時丟出 `ApiClientError('UNKNOWN', '無法連接伺服器，請稍後再試', res.status)`。重跑 Behave 全套回歸（10 features / 151 steps 全過）+ Playwright 對 4 個頁面（行事曆、帳戶、報表、新增收支）的完整 smoke test（含建立收支紀錄→報表即時反映→刪除清乾淨的全流程），確認修改沒有破壞既有頁面。

### Chrome E2E（Playwright，real backend，iPhone 14 viewport）

- 4 個頁面全部載入正常（行事曆、帳戶、報表、新增收支表單）
- 完整流程：新增一筆分類「餐飲」100% 的收支紀錄 → 報表頁即時反映（100%、正確金額）→ 刪除該筆 → 確認清乾淨
- 手動關閉後端模擬斷線 → 報表頁正確顯示「無法連接伺服器，請稍後再試」的友善錯誤訊息（而非原始 JS 例外）
- 全程 console error = 0

### 環境安全性

- 真實 `stock_analyzer.db` 的 `cash_position` 表全程維持 5 筆（測試前後一致）
- 測試建立的所有交易紀錄均已清除，Postgres 最終狀態：`ledger_transaction` 0 筆、`category` 17 筆

### 驗收點

- [x] 後端啟動且健康檢查通過（port 8001）
- [x] 前端 `MOCK_API=false` 且 rewrite proxy 正確指向 `http://localhost:8001`
- [x] 驗證矩陣 4 項通過 + 1 項 N/A（Auth，本專案無此機制）
- [x] Chrome E2E real 模式全數通過，含新發現並修正的錯誤處理 bug
