# Phase 07: Integration Validation ★

## 審查進度

- [x] 07.1 相關規格已審查 — **簽名**: 2026-08-24 22:45
- [x] 07.2 交付物已審查 — **簽名**: 2026-08-24 22:45

## 目的 (What)

驗證前端（Phase 06）與後端（Phase 05）透過真實 HTTP 連線能正確協作。

**這不是「加一個檢查」— 這是正式的 Phase**，有完整的 2 步審查。

來源：從 CRM 專案 6 個整合問題中提煉的 architectural fix。
兩條獨立 track 各自通過測試 ≠ 合在一起能跑。

核心動作：前端關閉 MSW mock → rewrite proxy → 打真實後端 API。

**依賴**：Phase 05 + Phase 06 都已在 `done/` 中。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | `specs/api.yml` | Phase 04 | 契約 = 驗證基準 |
| 2 | `web/src/lib/types/transaction.schema.ts` | Phase 06 | 前端型別，逐欄位比對 api.yml |
| 3 | Chrome Test Guard 測試計畫 | Phase 06 | 同一份測試計畫，換 real backend 重跑 |

## 環境

- 後端：systemd user service `ledger-app-backend`（`http://127.0.0.1:8001`），真實 PostgreSQL `ledger_app_dev`。驗證前已由上一個 session 重啟以套用代墊款修正碼，健康檢查 `{"status":"ok"}`。
- 前端：`web/.env.development` 已設 `NEXT_PUBLIC_MOCK_API=false` + `BACKEND_URL=http://localhost:8001`；本輪以 `npm run dev` 啟動（3000 埠被佔用，實際跑在 `http://localhost:3001`），驗證完成後已 `pkill -f "next dev"` 停止，未殘留 process。
- `stock-analyzer-api`（8100 埠）為真實下游系統，交易建立/刪除會同步/清理其 CashPosition；本輪所有測試交易皆透過 `DELETE /api/transactions/{id}` 刪除（而非直接動 DB），以觸發正確的 desync 清理。

## 交付物

| # | 交付物 | 內容 | 狀態 |
|---|--------|------|------|
| 07.1 | Response envelope + 欄位名一致性（curl 直打） | `POST /api/transactions`（含 `advancePaymentAmount`）、`GET /api/transactions/pending-advance-payments`、`POST .../settle-advance-payment`（含 422 金額不符、404 找不到交易）、`DELETE /api/transactions/{id}` 五種呼叫皆回傳與 `api.yml` 完全一致的 `{success, data}` / `{success, error:{message}}` 結構，欄位全 camelCase（`advancePaymentAmount`／`advancePaymentStatus`／`settlementTransactionId`） | DONE |
| 07.2 | 前後端型別比對 | `web/src/lib/types/transaction.schema.ts` 的 `TransactionSchema`／`SettleAdvancePaymentInputSchema`／`SettleAdvancePaymentResultSchema` 逐欄位比對真實後端回應與 `api.yml`，三方完全一致，無漂移 | DONE |
| 07.3 | Chrome E2E（real backend） | 用 `mcp__playwright__*` 完整跑過：新增支出（amount=4000, advancePaymentAmount=3000）→ 行事曆徽章 → 待收回清單 → 結清表單預填 3000 → 故意送 4000 觸發真實 422 → 修正送 3000 成功 → 從清單消失 → 行事曆徽章變「已收回」 | DONE |
| 07.4 | 報表數字驗證（real DB 聚合） | 結清後 `GET /api/reports/category-summary?startDate=2026-08-24&endDate=2026-08-24` 對餐飲類別回傳 `totalAmount: 1000.0`（= 4000 − 3000，非 0 非 4000） | DONE |
| 07.5 | 錯誤處理（4xx 在真實 UI 呈現） | 422 金額不符：UI 以 alert 顯示後端逐字訊息「還款金額與代墊金額不符，僅支援全額還款」；404（不存在的交易 id）：curl 直打確認回傳結構正確，UI 沒有可從清單頁面觸發此路徑的入口（清單只會列出真實存在的待收回項目），故此case僅以 API 層級驗證 | DONE |
| 07.6 | 測試資料清理 | curl 建立 2 筆（id 128, 129）+ 瀏覽器建立 2 筆（id 130, 131），全數以 `DELETE /api/transactions/{id}` 刪除，事後重查 `pending-advance-payments`、當日 `transactions`、當日 `category-summary` 三個端點均確認無殘留 | DONE |

### 驗收點

- [x] 後端啟動且健康檢查通過
- [x] 前端 `MOCK_API=false` 且 rewrite proxy 正確（`/api/*` → `BACKEND_URL`，實測請求確實落在 8001 後端）
- [x] 驗證矩陣 5 項全部通過（envelope／欄位一致性／Chrome E2E／報表數字／錯誤處理）
- [x] Chrome E2E real 模式全數通過（本輪 playwright MCP 未出現先前的 profile 鎖定問題）
- [x] 所有測試資料已透過 API 刪除並重查確認清理乾淨

## 詳細驗證紀錄（2026-08-24 22:45）

### 1. Response envelope（curl 直打真實後端）

```
POST /api/transactions {amount:4000, advancePaymentAmount:3000, categoryId:1, accountId:1, type:支出}
→ 201-equivalent {"success":true,"data":{"id":128,...,"advancePaymentAmount":3000.0,"advancePaymentStatus":"pending","settlementTransactionId":null}}

GET /api/transactions/pending-advance-payments
→ {"success":true,"data":[{...id:128...}]}

POST /api/transactions/128/settle-advance-payment {date, amount:4000（故意錯）, accountId:1}
→ HTTP 422 {"success":false,"error":{"message":"還款金額與代墊金額不符，僅支援全額還款"}}

POST /api/transactions/128/settle-advance-payment {date, amount:3000（正確）, accountId:1}
→ HTTP 200 {"success":true,"data":{"settlementTransaction":{...id:129,type:收入,amount:3000...},"advancePaymentTransaction":{...id:128,advancePaymentStatus:"settled",settlementTransactionId:129}}}

POST /api/transactions/999999/settle-advance-payment
→ HTTP 404 {"success":false,"error":{"message":"找不到該筆收支紀錄"}}
```

所有欄位名、巢狀結構、HTTP status 與 `specs/api.yml` 的 `TransactionResponse`／`SettleAdvancePaymentResponse`／`ErrorResponse` schema 完全一致。

### 2. 欄位名一致性

`web/src/lib/types/transaction.schema.ts` 的 `TransactionSchema` 欄位（`advancePaymentAmount: number|null`、`advancePaymentStatus: 'pending'|'settled'|null`、`settlementTransactionId: number|null`）與上述真實後端回應逐一比對，**完全一致，無漂移**。這是本次驗證的重點之一——Phase 05/06 各自修正過兩輪，仍需確認兩輪修正沒有各自收斂到不同的欄位語意上，結果確認一致。

### 3. Chrome E2E（real backend，`http://localhost:3001`，`NEXT_PUBLIC_MOCK_API=false`）

1. `/transactions/new`：類型預設支出，選分類「餐飲」、金額 4000、帳戶「永豐銀行」、代墊金額 3000、備註 `[phase07-integration-test — safe to delete]`，送出成功，導向 `/calendar`，新交易 id=130。
2. `/calendar` 當日列表出現該筆，徽章顯示「代墊款 $3,000 · 待收回」，金額顯示 −4,000（未結清前全額計入，符合規格）。
3. `/transactions/pending-advance-payments`：清單正確顯示「總額 $4,000」／「（代墊 $3,000）」。
4. 點「確認收到還款」展開表單，**還款金額欄位預填 3000（非 4000）**——確認 Phase 06 修正的核心邏輯在真實後端下仍正確。
5. 故意改成 4000 送出 → UI 以 alert 顯示後端逐字錯誤訊息「還款金額與代墊金額不符，僅支援全額還款」，`browser_console_messages(level="error")` 記錄到預期中的一筆 `422 (Unprocessable Content)` network 錯誤，非未預期的程式錯誤。
6. 改回 3000、選帳戶「永豐銀行」送出 → 成功，清單變為「目前沒有待收回的代墊款」（該筆從待收回清單消失）。新建立的結清交易 id=131。
7. 回到 `/calendar`，該筆徽章更新為「代墊款 $3,000 · 已收回」。
8. 全程 console error 計數僅 1（步驟 5 那筆預期中的 422），無其他未預期錯誤。

### 4. 報表數字（real DB 聚合）

結清後：
```
GET /api/reports/category-summary?startDate=2026-08-24&endDate=2026-08-24
→ {"success":true,"data":[{"category":"餐飲","totalAmount":1000.0}]}
```
確認為 `amount(4000) − advancePaymentAmount(3000) = 1000`，非 0（完全排除）也非 4000（完全計入），符合規格「已結清後計入支出的有效金額變成 amount − advancePaymentAmount」。也在 `/reports` 頁面實際瀏覽（2026 August 月報表）確認餐飲類別合計含入此筆的淨額貢獻，未見異常。

### 5. 錯誤處理

- 422（金額不符）：見上方 Chrome E2E 步驟 5，UI 呈現正確、訊息逐字正確。
- 404（不存在的交易 id）：以 curl 直打 `POST /api/transactions/999999/settle-advance-payment` 確認回傳結構正確（`{success:false, error:{message:"找不到該筆收支紀錄"}}`，HTTP 404）。此路徑在目前 UI 中無法從正常操作流程觸發（待收回清單只會列出真實存在的項目，沒有「輸入任意 id」的入口），故僅在 API 層級驗證，不構成缺陷。

### 測試資料與清理紀錄

| id | 建立方式 | 內容 | 刪除方式 | 刪除結果 |
|----|---------|------|---------|---------|
| 128 | curl | 支出 4000／代墊 3000（餐飲／永豐銀行） | `DELETE /api/transactions/128` | `{"success":true}` HTTP 200 |
| 129 | curl（settle 128 產生） | 收入 3000（結清交易） | `DELETE /api/transactions/129` | `{"success":true}` HTTP 200 |
| 130 | 瀏覽器（Chrome E2E） | 支出 4000／代墊 3000（餐飲／永豐銀行） | `DELETE /api/transactions/130` | `{"success":true}` HTTP 200 |
| 131 | 瀏覽器（settle 130 產生） | 收入 3000（結清交易） | `DELETE /api/transactions/131` | `{"success":true}` HTTP 200 |

事後重查確認清理乾淨：
- `GET /api/transactions/pending-advance-payments` → `{"success":true,"data":[]}`
- `GET /api/transactions?startDate=2026-08-24&endDate=2026-08-24` → 9 筆（皆為既有真實資料，無 `phase07` 標記殘留）
- `GET /api/reports/category-summary?startDate=2026-08-24&endDate=2026-08-24` → `{"success":true,"data":[]}`（今日無任何資料，測試貢獻的 1000 已完全隨交易刪除而消失）

四筆刪除呼叫全數成功，無需走「STOP 並回報清理失敗」的路徑。

### 結論

前端（真實模式）與後端（真實 PostgreSQL）之間的代墊款完整流程——建立混合代墊交易、行事曆徽章、待收回清單雙金額顯示、結清表單正確預填代墊金額（而非總金額）、後端 422 錯誤訊息正確透傳到 UI、結清成功後清單與徽章同步更新、報表聚合正確反映淨額——**全數在真實 HTTP 連線下驗證通過，無 mock 掩蓋的契約落差**。Phase 05／06 各自的兩輪修正在整合後彼此一致，未發現新的整合層 bug。
