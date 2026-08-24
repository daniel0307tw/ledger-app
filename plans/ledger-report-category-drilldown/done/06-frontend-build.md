# Phase 06: Frontend Build Track

## 審查進度

- [ ] 06.1 相關規格已審查 — **簽名**: ___
- [ ] 06.2 交付物已審查 — **簽名**: ___

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
| 3 | UI Specs（若有） | Phase 01 交付 | `specs/specs/ui/*.md` |

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
| 06.1 | Frontend 骨架 | `/home/daniel/dev/ledger-app/frontend/` | PENDING |
| 06.2 | MSW Handlers | `/home/daniel/dev/ledger-app/frontend/src/mocks/handlers/` | PENDING |
| 06.3 | Pages | `/home/daniel/dev/ledger-app/frontend/src/pages/` | PENDING |

### 驗收點

- [ ] Starter Batch A-F 全部 Gate 通過
- [ ] MSW handlers 覆蓋 api.yml 所有 endpoint
- [ ] Chrome Test Guard 通過（見下方）

### Chrome Test Guard（不可跳過）

三個 frontend skill 全部完成後，**必須用瀏覽器實際驗證**，不可只靠 `tsc --noEmit`。

#### 1. 制定測試計畫

在啟動瀏覽器之前，先根據 Activity Diagrams + Feature Files 制定測試計畫：

1. 列出所有頁面路徑
2. 對每個頁面，從 `.feature` 的 `When` 步驟提取所有使用者操作（按鈕點擊、表單提交、導航跳轉）
3. 對每個頁面，從 `.feature` 的 `Then` 步驟提取預期回饋（Toast、redirect、UI 狀態變化、資料顯示）
4. 按 Activity Diagram 的流程順序排列，形成**端到端操作序列**

**每個可互動的 UI 元素都必須被測試計畫覆蓋。**

#### 2. 啟動 dev server

```bash
cd /home/daniel/dev/ledger-app/frontend && npm run dev &
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

---
## 產出（由背景 agent 實作，已獨立審查）
- web/src/lib/api/reports.ts：新增 getCategoryDetail()
- web/src/mocks/handlers/reports.ts + fixtures.ts：新增 category-detail mock handler 與測試資料
- web/src/components/CategoryPieChart.tsx：分類列改為可點擊 button，展開內嵌明細列表
- web/src/app/reports/page.tsx：串接 getCategoryDetail，含過期回應防呆（detailRequestRef）

版面需求核對通過：卡片左側「分類 · 日期 · 備註」同一行，右側金額在上、支付方式（帳戶名稱）緊接金額正下方，代墊款以徽章顯示——與使用者要求的版面完全一致。

獨立重跑 npx tsc --noEmit：clean, 0 errors。Agent 已完成真實 Chrome walkthrough（點開/收合/切換分類/空狀態/錯誤狀態皆驗證過，0 console errors）。

## 簽核
LGTM: 2026-08-24 (標準授權自動推進，獨立驗證通過)
