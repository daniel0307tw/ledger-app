# Phase 06: Frontend Build Track

## 審查進度

- [x] 06.1 相關規格已審查 — **簽名**: 2026-08-23 17:18
- [x] 06.2 交付物已審查 — **簽名**: 2026-08-23 17:18

## 目的 (What)

以 Phase 04 的 api.yml + Phase 01 的 Activity Diagram 為輸入，
建立前端基礎建設（MSW Starter）、API 層（MSW handlers）、頁面實作。

**雙模式運作**：依 Execution Plan 的 IMPL_IMPACT 決定走哪種模式。

| 模式 | 觸發條件 | 行為 |
|------|---------|------|
| **One-shot Build** | 該 endpoint 的 IMPL_IMPACT 只有 `NEW_OPERATION` 或無 | 完整 Starter → MSW → Pages |
| **Targeted Fix** | 該 endpoint 有具體 impact type（`ENDPOINT_SCHEMA` / `ENDPOINT_ROUTE`） | 定位受影響的 MSW handler / Page → 定向修復 |

**依賴**：Phase 04 必須在 `done/` 中。
**可與 Phase 05 平行**：兩者只依賴 Phase 04，互不依賴。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | api.yml | Phase 04 交付 | API 契約 — MSW handlers 的生成依據 |
| 2 | Activity Diagrams | Phase 01 交付 | 流程結構（路線、分支）— 頁面導航的依據 |
| 3 | UI Specs（若有） | Phase 01 交付 | `/home/daniel/dev/ledger-app/specs/ui/*.md` |

## 交付物

carry-on Step 06.2 觸發時：

1. 讀取 Execution Plan 的 IMPL_IMPACT（Phase 06 區段）

### One-shot Build（正常模式）

| 順序 | Skill | 做什麼 | 前提 |
|------|-------|--------|------|
| 1 | `/aibdd-auto-frontend-apifirst-msw-starter` | 前端骨架 Batch A-F + Gate A-F | — |
| 2 | `/aibdd-auto-frontend-msw-api-layer` | 從 api.yml 產生 MSW handlers | Starter 完成 |
| 3 | `/aibdd-auto-frontend-nextjs-pages` | 頁面 + UI 實作 | API Layer 完成 |

### Targeted Fix（定向修復模式）

| Impact Type | 修復動作 |
|-------------|---------|
| `ENDPOINT_SCHEMA` | 更新 MSW handler mock data + 前端 type 定義 + 受影響的 Page component |
| `ENDPOINT_ROUTE` | 更新 MSW handler path + Frontend fetch URL + Next.js rewrite 規則 |

### Starter Gate 驗證重點（Batch A-F）

- **Gate A**：`npm install` 通過、`next.config.mjs` rewrites 存在、`BACKEND_URL` 在 `.env`
- **Gate D**：`MOCK_API=true` → MSW 攔截；`MOCK_API=false` → rewrite proxy 到後端
- 詳見 `/aibdd-auto-frontend-apifirst-msw-starter` 的 `references/batch-gates.md`

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 06.1 | Frontend 骨架 | `/home/daniel/dev/ledger-app/web/` | DONE |
| 06.2 | MSW Handlers | `/home/daniel/dev/ledger-app/web/src/mocks/handlers/` | DONE |
| 06.3 | Pages | `/home/daniel/dev/ledger-app/web/src/app/` | DONE |

### 驗收點

- [x] Starter Batch A-F 全部 Gate 通過（本輪 starter 稍早已建好）
- [x] MSW handlers 覆蓋 api.yml 所有 endpoint
- [x] Chrome Test Guard 通過（見下方，改用 Playwright CLI 執行）

### Chrome Test Guard（不可跳過）— 實際執行記錄

**環境沒有 `mcp__claude-in-chrome__*` 工具**，改用專案本身已有的 `@playwright/test` 依賴，寫一支腳本用真正的 headless Chromium（390×844，iPhone 尺寸）跑過完整流程：安裝 `npx playwright install chromium`（無 sudo，跳過系統依賴安裝，僅裝瀏覽器二進位檔）後執行。

**跑過的流程**：行事曆頁載入 → 切到帳戶頁確認 fixtures（永豐銀行/新光銀行）→ 新增帳戶（玉山銀行）→ 點 FAB 新增收支紀錄 → 填表送出 → 確認出現在當日清單 → 點該筆紀錄確認編輯表單正確帶入既有資料 → 刪除 → 轉帳流程（選帳戶/填金額/送出）。

**發現並修復的真實 bug**：第一次載入時畫面上直接顯示了 `Unexpected token 'F', "Forbidden" is not valid JSON` 錯誤（而非只是 console 雜訊）。根因是 React Strict Mode 在 dev 模式下把 `MSWProvider` 的 effect 呼叫兩次，第二次呼叫 MSW 的 `worker.start()` 因為「network already enabled」丟例外，這個例外被吞掉後直接 `setReady(true)`，導致頁面在 service worker 真正接管、開始攔截請求之前就掛載去發請求，打到真實的 Next.js rewrite proxy（後端沒在跑）得到 403 Forbidden 的 HTML。修法：`MSWProvider` 改用 module-level 的 singleton promise 統一兩次 effect 呼叫的初始化流程，並在 `worker.start()` resolve 後額外等待 `navigator.serviceWorker.controller` 真的被設定（或 `controllerchange` 事件）才放行子元件。修復後重跑整套流程，console 完全乾淨（0 error），並用 `page.on('response')` 確認所有 API 請求都拿到 200。

原本的方法（三階段）：

#### 1. 制定測試計畫

在啟動瀏覽器之前，先根據 Activity Diagrams + Feature Files 制定測試計畫：

1. 列出所有頁面路徑
2. 對每個頁面，從 `.feature` 的 `When` 步驟提取所有使用者操作（按鈕點擊、表單提交、導航跳轉）
3. 對每個頁面，從 `.feature` 的 `Then` 步驟提取預期回饋（Toast、redirect、UI 狀態變化、資料顯示）
4. 按 Activity Diagram 的流程順序排列，形成**端到端操作序列**

**每個可互動的 UI 元素都必須被測試計畫覆蓋。**

#### 2. 啟動 dev server

```bash
cd /home/daniel/dev/ledger-app/web && npm run dev &
```

背景執行，等待 server ready。

#### 3. 逐步執行測試計畫

使用 `mcp__claude-in-chrome__*` 工具，**按測試計畫逐步操作**：

1. 對每個頁面路徑：`navigate` → 確認頁面載入成功（無白屏）
2. 讀取 `console messages`：確認無 error 層級訊息
3. 對每個可互動元素（按鈕、輸入框、連結）：**實際點擊 / 填寫 / 提交**
4. 對每個操作後的預期回饋：確認 UI 正確更新

**測試計畫中的每個步驟都必須實際執行，不可跳過。**

#### 4. 發現 bug → 立即修復 → 重新驗證

- 發現 console error → 讀取錯誤訊息 → 定位問題 → 修改程式碼 → 重新整理頁面 → 驗證修復
- 發現 UI 不如預期 → 修改元件 → 重新整理頁面 → 驗證修復
- **修復後必須從頭重跑受影響的測試步驟**，確認無級聯破壞
- 重複此迴圈直到所有步驟全部通過

#### 5. 全部通過後停止 dev server

所有測試計畫步驟通過、console 無 error → 停止 dev server → 驗收完成。
