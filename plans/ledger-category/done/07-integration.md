# Phase 07: Integration Validation ★

## 審查進度

- [x] 07.1 相關規格已審查 — **簽名**: 2026-08-23 19:54
- [x] 07.2 交付物已審查 — **簽名**: 2026-08-23 19:54

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
| 07.2 | 驗證矩陣通過紀錄 | 5/5 全通過 | DONE |

### 驗收點

- [x] 後端啟動且健康檢查通過（port 8001，`GET /api/categories` 回傳 17 筆）
- [x] 前端 `MOCK_API=false` 且 rewrite proxy 正確（`.env.development` 已指向 `BACKEND_URL=http://localhost:8001`）
- [x] 驗證矩陣 5 項全部通過（見下方紀錄）
- [x] Chrome E2E real 模式全數通過（10 步驟流程，console 0 error，斷言 0 error）

### 實際執行紀錄

**驗證矩陣（5/5）**：
1. Response envelope：`{success, data}` / `{success, error:{message}}` 一致 — PASS
2. 欄位名一致性：`categoryId`/`accountId`/`isTransfer`/`transferGroupId`/`syncStatus`/`cashPositionId` 前後端與 api.yml 三方一致 — PASS
3. Query params：`GET /api/transactions?startDate=&endDate=` 正確過濾 — PASS
4. Error handling：分類不存在 → 404 `找不到該分類`；缺必要參數 → 400 `必要參數未提供` — PASS
5. Auth flow：本專案無 auth（單人使用），不適用，Clear（N/A）

**Chrome E2E（Playwright，real backend，10 步驟）**：
calendar 載入 → accounts 載入 → 開啟 CategoryPicker（17 選項）→ inline 新增分類並自動選中 → 送出交易（201，categoryId 正確）→ 行事曆顯示新分類名稱 → 編輯頁分類正確帶入 → 改選既有分類「餐飲」並儲存（200）→ 刪除交易（200，正確顯示空狀態）→ 轉帳入口確認存在。全程 console error = 0。

**外部系統安全性重驗**：後端行程的 `CASH_POSITION_DB_PATH` 確認指向隔離的 scratchpad SQLite（非真實檔案）；真實 `/home/daniel/stock_analyzer/data/stock_analyzer.db` 的 `cash_position` 資料表列數全程維持 5 筆（測試前後一致）。

**測試資料清理**：測試建立的分類（id 21/22/23）與交易均已清除，Postgres `category` 表最終回到乾淨的 17 筆、`ledger_transaction` 表回到 0 筆。

**未停止 dev server**：Phase 07 範本原本建議驗證完成後停止 dev server，但目前這組 backend(8001)/frontend(3001) 是 daniel 手機日常實際在用的服務（非本輪新啟動），故保留運行，未依範本關閉，避免中斷實際使用。
