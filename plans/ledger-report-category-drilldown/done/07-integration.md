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
## 產出（由背景 agent 執行真後端+真前端整合驗證，已獨立複查）
- 後端 systemd 服務已重啟載入新程式碼，確認 active
- 真前端（web/.env.development，NEXT_PUBLIC_MOCK_API=false）→ next.config.js rewrite → 真後端（127.0.0.1:8001）→ 真 Postgres（ledger_app_dev）全鏈路驗證通過
- Chrome 實測：8 月「餐飲」「日常用品」兩個分類皆點開驗證，明細逐筆比對 curl 結果一致，帳戶名稱正確解析，版面（分類·日期·備註同行；金額 + 帳戶名稱在金額正下方）與需求一致，切換分類無殘留資料，0 console errors
- 純讀取功能，未寫入任何測試資料到真實資料庫（前後比對 5 筆 id 完全相同：20/21/54/49/48）
- tsc --noEmit clean；前端 dev server 已關閉，port 已釋放

獨立複查：systemctl --user is-active ledger-app-backend → active；重新 curl 同一 endpoint → 同樣 5 筆 id，資料庫無殘留。

## 簽核
LGTM: 2026-08-24 (標準授權自動推進，獨立驗證通過)
