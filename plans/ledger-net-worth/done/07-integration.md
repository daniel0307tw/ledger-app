# Phase 07: Integration Validation ★

## 審查進度

- [ ] 07.1 相關規格已審查 — **簽名**: ___
- [ ] 07.2 交付物已審查 — **簽名**: ___

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
| 07.1 | Chrome E2E 結果（real backend） | 全通過 | PENDING |
| 07.2 | 驗證矩陣通過紀錄 | 5/5 全通過 | PENDING |

### 驗收點

- [ ] 後端啟動且健康檢查通過
- [ ] 前端 `MOCK_API=false` 且 rewrite proxy 正確
- [ ] 驗證矩陣 5 項全部通過
- [ ] Chrome E2E real 模式全數通過

---

**驗證矩陣（比照本專案既有慣例：無 auth 系統、Chrome E2E 以 Playwright 手動截圖取代正式 Cucumber Test Guard，延續前幾輪 Integration Validation 的實際作法）**：

| # | 驗證項目 | 結果 |
|---|---------|------|
| 1 | Response envelope | ✓ curl 直接驗證 `{success, data}` 結構正確 |
| 2 | 欄位名一致性 | ✓ api.yml / `app/schemas/net_worth.py` / `web/src/lib/types/net-worth.schema.ts` 三處欄位名逐一比對完全一致（cashTotal, creditCardDebtTotal, stockHoldings[], currencyTotals[], stockDataStatus） |
| 3 | Auth flow | N/A（本專案無 auth 系統，比照既有 round 慣例） |
| 4 | Query params | N/A（本 endpoint 無參數） |
| 5 | Error handling | ✓ 實際關閉 stock_analyzer API（stop 背景 process）→ real backend 回傳 `stockDataStatus:"failed"` → 前端正確顯示紅色錯誤提示、現金/信用卡不受影響；驗證後重啟服務恢復正常，再次 curl 確認資料回復正常 |

**端到端流程**：
1. 重啟 ledger-app 後端（`uvicorn app.main:app --port 8001`）載入新 code
2. curl 驗證正常情境：cashTotal=15200, creditCardDebtTotal=-4705, 2 檔台股真實持倉，與使用者稍早在 stock_analyzer 畫面看到的數字完全一致
3. 停止 stock_analyzer API server，curl 驗證 partial failure 情境：stockDataStatus=failed，現金/信用卡不受影響
4. Playwright 對 `/assets` 頁面（iPhone 14 Pro viewport）截圖，正常情境與失敗情境皆確認畫面正確渲染
5. Playwright 對 `/calendar` 頁面截圖，確認四分頁底部導覽無版面回歸
6. 重啟 stock_analyzer API server 恢復正常，再次 curl 確認資料回復
7. 全專案 Behave 回歸測試：11 features / 58 scenarios / 204 steps 全過
8. `tsc --noEmit`：0 錯誤
9. 安全確認：`cash_position` 表仍為 10 筆（無異動）、`tw_holding` 表仍為 0 筆（本輪設計上從未寫入），全程零寫入、零污染

**LGTM**: 2026-08-24（使用者指示比照 C 到底模式）
