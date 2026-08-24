# Phase 07: Integration Validation ★

## 審查進度

- [x] 07.1 相關規格已審查 — **簽名**: 2026-08-23 18:45
- [x] 07.2 交付物已審查 — **簽名**: 2026-08-23 18:45

## 執行紀錄

### 環境

- Postgres：本機 docker-compose（`ledger-app-postgres`，port 5432），`alembic upgrade head` 建表成功。
- Backend：`uvicorn app.main:app --port 8001`（8000 被機器上另一個既有服務占用，改用 8001；前端 `BACKEND_URL` 對應調整）。
- CashPosition 外部 DB：**特別用隔離的暫存 SQLite 檔案**（`/tmp/.../cash_position_integration.db`，schema 比照 stock_analyzer 真實表），透過 `CASH_POSITION_DB_PATH` 環境變數覆寫，全程不觸碰 `/home/daniel/stock_analyzer/data/stock_analyzer.db`（驗證前後 row count 皆為 5，未變動）。
- Frontend：`web/.env.development` 改 `NEXT_PUBLIC_MOCK_API=false`、`BACKEND_URL=http://localhost:8001`，`next dev -p 3001`。

### 發現並修正的真實 bug

**`app/main.py` 的 `create_app()` 從未初始化 DB session factory。** `app/core/deps.py` 的 `get_db()` 依賴模組層級的 `_session_factory`，只有 Behave 測試的 `tests/features/environment.py::before_all` 會呼叫 `set_session_factory()`。真正用 `uvicorn` 啟動時完全沒有等效邏輯，任何打 DB 的 endpoint 一律 500（`RuntimeError: Session factory not initialized`）。這正是兩條獨立通過測試的 track（Backend TDD 用測試自己接的 session factory；Frontend Build 用 MSW mock）合起來才會暴露的整合缺口。

修正：在 `create_app()` 內加上 FastAPI `startup` event，從 `settings.DATABASE_URL` 建立 engine 並呼叫 `set_session_factory()`。修正後重跑 Behave 全套（7 features / 31 scenarios / 109 steps）仍全數通過，確認未破壞既有測試（`TestClient(app)` 非 context-manager 用法不會觸發 startup event，測試自己的 session factory 設定仍生效）。

### 驗證矩陣（5/5 全通過）

| # | 項目 | 結果 |
|---|------|------|
| 1 | Response envelope 格式 | `{success, data}` / `{success, error:{message}}` 皆正確 |
| 2 | 欄位名一致性 | 前端 camelCase（`accountId`/`isTransfer`/`syncStatus`/`cashPositionId`）與後端回應、api.yml 一致 |
| 3 | Auth flow | N/A — 本專案無登入機制（單人使用，MVP 明確排除） |
| 4 | Query params 完整性 | `startDate`/`endDate` 區間查詢正確 |
| 5 | Error handling | 缺必填欄位 → 400「必要參數未提供」；帳戶不存在 → 404「找不到該帳戶」；金額為負 → 400「金額必須為正數」，前端皆正確顯示 |

### Chrome E2E（real backend mode）

沿用 Phase 06 相同的 Playwright 腳本（改打 `localhost:3001` real backend），走完整流程：行事曆載入 → 帳戶列表 → 新增收支紀錄 → 當日清單顯示 → 點擊進編輯（欄位正確帶入）→ 刪除 → 轉帳（轉出+轉入兩筆，`transferGroupId` 相同）。

結果：console errors `(none)`，8 張截圖畫面正常。轉帳同步、刪除沖銷皆以真實 API + 真實 Postgres + 隔離 CashPosition SQLite 驗證正確（轉帳後 CashPosition 兩邊分別 Withdraw/Deposit 各一筆；刪除交易後對應 CashPosition 紀錄一併移除）。

測試期間建立的資料已透過 API 清除（transactions），僅留下 永豐銀行/新光銀行 兩個帳戶作為初始資料（無 DELETE /api/accounts endpoint，且此為合理的起始種子資料）。

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
| 07.1 | Chrome E2E 結果（real backend） | 全通過 | PENDING |
| 07.2 | 驗證矩陣通過紀錄 | 5/5 全通過 | PENDING |

### 驗收點

- [ ] 後端啟動且健康檢查通過
- [ ] 前端 `MOCK_API=false` 且 rewrite proxy 正確
- [ ] 驗證矩陣 5 項全部通過
- [ ] Chrome E2E real 模式全數通過
