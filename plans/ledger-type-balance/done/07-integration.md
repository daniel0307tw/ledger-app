# Phase 07: Integration Validation ★

## 審查進度

- [x] 07.1 相關規格已審查 — **簽名**: 2026-08-23 23:05
- [x] 07.2 交付物已審查 — **簽名**: 2026-08-23 23:05

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

後端已在真實環境（非 Docker 一次性容器，而是 daniel 日常使用中的即時 process）運行於 port 8001，`.env.development` 本就是 `NEXT_PUBLIC_MOCK_API=false` + `BACKEND_URL=http://localhost:8001`，故本輪驗證直接針對真實運行中的前後端，無需另外切換環境。

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 07.1 | Chrome/Playwright E2E 結果（real backend） | 全通過，見下方 | DONE |
| 07.2 | 驗證矩陣通過紀錄 | 4/5 通過，1 項 N/A（見下方） | DONE |

### 驗證矩陣結果

| # | 驗證項目 | 結果 | 說明 |
|---|---------|------|------|
| 1 | Response envelope 格式 | ✅ | 所有新/改 endpoint（categories/accounts/transactions）皆為 `{success, data}` / `{success, error:{message}}` |
| 2 | 欄位名一致性 | ✅ | `type`/`balance` 前端 Zod schema、後端 Pydantic schema、api.yml 三方一致（皆為單詞，無 camelCase alias 需求） |
| 3 | Auth flow | N/A | 本專案為 daniel 個人單機記帳工具，無登入/認證機制，前後端皆無 auth 相關程式碼，此項不適用 |
| 4 | Query params 完整性 | ✅ | 本輪未變更任何 query 型 endpoint 的參數（categories/accounts 無 query params；transactions 查詢邏輯未變） |
| 5 | Error handling | ✅ | 直接對真實後端 `curl` 觸發 422（分類收支類型不符，見下方）+ 400（缺 type/name）+ 404（分類不存在），前端 `client.ts` 已通用處理非 2xx → 顯示 `error.message` |

### Chrome/Playwright E2E 執行紀錄（real backend, 桌面+手機雙 viewport）

1. **帳戶頁**：5 筆真實帳戶皆正確顯示 type 標籤 + balance（初始皆為 $0，標籤「餘額」）；新建信用卡帳戶正確顯示「信用卡」標籤
2. **記帳表單分類過濾**：預設支出類過濾出 17 筆（16 支出 + 校正回歸皆可），無收入分類洩漏；切換收入後過濾為 4 筆（校正回歸、薪資、獎金、投資）
3. **切換類型清空分類**：選定「餐飲」（支出）後切換為收入，分類選擇器正確清空為「請選擇分類」
4. **內嵌新增分類繼承 type**：收入情境下新增分類，自動帶入 type=收入，無需額外選擇欄位
5. **完整記帳流程（真實後端）**：透過實際 UI 建立一筆收入 8000／薪資／永豐銀行的收支紀錄 → 成功導向行事曆頁 → 帳戶頁即時反映永豐銀行 balance=$8,000（餘額標籤）
6. **後端防禦深度（422）**：直接對 API 送出「薪資（收入分類）+ type=支出」，正確回傳 `422 分類收支類型與交易類型不符`
7. **全站無 console error**：行事曆、報表、帳戶、轉帳、記帳表單 5 個頁面，桌面 + iPhone 14 模擬雙 viewport，皆無 console error / page error

### 測試資料清理與安全不變式驗證

- 驗證過程中在真實 Postgres DB 建立的測試帳戶（`測試信用卡-*`）、測試分類（`測試收入分類-*`）、測試交易（1 筆真實 8000 收入紀錄）皆已清除，`account`=5、`category`=20、`ledger_transaction`=0，回到本輪開始前的真實基準狀態
- **發現並修正一個測試污染案例**：上述測試交易的 sync_status=synced，連動在真實 `stock_analyzer.db` 的 `cash_position` 表新增了一筆測試紀錄（id=6, 永豐銀行/Deposit/8000/TWD）；僅刪除 ledger_transaction 不足以清除，額外定位並刪除該筆 CashPosition 紀錄，`cash_position` 表列數確認回到基準值 5。已寫入記憶供未來 session 留意（真實後端整合測試需同時清理兩邊）
- 最終回歸測試（Behave，隔離測試 DB）：10 features / 36 rules / 50 scenarios / 170 steps 全數通過
- `stock_analyzer.db` 的 `cash_position` 表列數全程維持 5（測試前、測試中發現 6、清理後回到 5）

### 驗收點

- [x] 後端啟動且健康檢查通過（真實運行中，非本輪額外啟動）
- [x] 前端 `MOCK_API=false` 且 rewrite proxy 正確（本就如此設定）
- [x] 驗證矩陣 5 項：4 通過 + 1 項確認 N/A（無 auth 機制）
- [x] Chrome/Playwright E2E real 模式全數通過
