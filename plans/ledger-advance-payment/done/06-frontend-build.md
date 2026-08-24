# Phase 06: Frontend Build Track

## 審查進度

- [x] 06.1 相關規格已審查 — **簽名**: 2026-08-24 22:15
- [x] 06.2 交付物已審查 — **簽名**: 2026-08-24 22:15

## 修正記錄（2026-08-24 22:15）

**背景**：同 Phase 05 卡片所述，第一輪誤用 boolean `isAdvancePayment` 全有全無模型，本輪修正為
`advancePaymentAmount: number | null`（交易金額中屬於代墊款的部分）。前端所有型別、mock、表單、頁面
逐一比照後端修正後的欄位語意調整，且此輪額外修正了第一輪遺留的「編輯頁不支援代墊款欄位」缺口——因為
後端 `update_transaction` 現在已支援編輯 `advancePaymentAmount`（見 Phase 05 卡片項目 6），對應的前端
`showAdvancePayment={false}` 限制已不再需要，故移除。

## 目的 (What)

以 Phase 04 的 api.yml + Phase 01 的 Activity Diagram 為輸入，
建立前端基礎建設（MSW Starter）、API 層（MSW handlers）、頁面實作。

**本專案實際狀況**：前端骨架（Next.js App Router + MSW + Zod）已存在（非 greenfield），
本 Phase 屬於 **Targeted Fix** 模式——在既有 `web/` 專案上針對「代墊款」功能新增/修改型別、
API client、MSW handlers、表單與頁面，不重跑 Starter skill。

## 相關規格

| # | 規格 | 來源 | 說明 |
|---|------|------|------|
| 1 | `specs/api.yml` | Phase 04 交付 | API 契約（`isAdvancePayment` / `advancePaymentStatus` / `settlementTransactionId`、`SettleAdvancePaymentInput/Response`、`POST /api/transactions/{id}/settle-advance-payment`、`GET /api/transactions/pending-advance-payments`） |
| 2 | `tests/features/transactions/新增收支紀錄.feature` | Phase 03 交付 | isAdvancePayment 僅限支出 Rule + Example |
| 3 | `tests/features/transactions/確認收到還款.feature` | Phase 03 交付 | 5 種錯誤情境（不存在／非代墊款／已結清／金額不符／帳戶不存在）+ 成功情境，含逐字錯誤訊息 |
| 4 | `tests/features/transactions/查詢待收回代墊款清單.feature` | Phase 03 交付 | 空清單／populated 清單情境 |

## 交付物

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 06.1 | Zod Types | `web/src/lib/types/transaction.schema.ts`（modify：`isAdvancePayment: boolean` → `advancePaymentAmount: number \| null`，`TransactionInputSchema` 對應欄位改為 `.positive().nullable().optional()`） | DONE |
| 06.2 | API Client | `web/src/lib/api/transactions.ts`（不需改，JSON 透傳，欄位改名不影響此檔） | DONE |
| 06.3 | MSW Handlers | `web/src/mocks/handlers/transactions.ts`（modify：`validateInput` 加代墊金額不可超過總金額檢查；create/update 改用 `advancePaymentAmount`；update 新增「已結清交易若 amount 或 advancePaymentAmount 變動則自動改回 pending」邏輯（第一輪遺漏）；pending 清單與 settle 端點的比對/建立金額改用 `advancePaymentAmount`（settle 檢查金額比對對象從 `transaction.amount` 改為 `transaction.advancePaymentAmount`）） | DONE |
| 06.4 | MSW Fixtures | `web/src/mocks/fixtures.ts`（modify：id=1~3 的 `isAdvancePayment: false` → `advancePaymentAmount: null`；id=4 從純 boolean pending 範例改為混合情境範例：amount=4000、advancePaymentAmount=3000、status=pending，對應 feature 檔的具體 Example） | DONE |
| 06.5 | 型別修正（連帶） | `web/src/mocks/handlers/transfers.ts`（modify：2 處 `Transaction` 物件字面量的 `isAdvancePayment: false` → `advancePaymentAmount: null`） | DONE |
| 06.6 | 交易表單 | `web/src/components/TransactionForm.tsx`（modify：checkbox 改為數字輸入框「代墊金額」；type=支出 時才顯示；client-side 驗證代墊金額不可超過總金額；切到收入時自動清空） | DONE |
| 06.7 | 新增/編輯頁面 | `web/src/app/transactions/new/page.tsx`（不需改）、`web/src/app/transactions/[id]/edit/page.tsx`（modify：**移除** `showAdvancePayment={false}` 限制——後端 `update_transaction` 本輪已支援 `advance_payment_amount`（見 Phase05 卡片項目 6），編輯頁改為從 URL query 帶入 `advancePaymentAmount` 初始值並允許編輯） | DONE |
| 06.8 | 交易列表狀態顯示 | `web/src/app/calendar/page.tsx`（modify：徽章判斷條件從 `t.isAdvancePayment` 改為 `t.advancePaymentAmount != null`，徽章文字加上代墊金額數字；編輯連結的 query string 補上 `advancePaymentAmount` 供編輯頁預填） | DONE |
| 06.9 | 待收回代墊款頁面 | `web/src/app/transactions/pending-advance-payments/page.tsx`（modify：**核心修正**——`openSettleForm` 預帶值從 `t.amount` 改為 `t.advancePaymentAmount`；清單顯示從單一金額改為「總額 $4,000（代墊 $3,000）」雙欄顯示） | DONE |
| 06.10 | 導覽連結 | `web/src/app/settings/page.tsx`（不需改，第一輪已完成且與本次修正無關） | DONE |

### 驗收點

- [x] `npx tsc --noEmit`（於 `web/` 執行）零錯誤
- [x] MSW handlers 覆蓋 api.yml 本次新增的 2 個 endpoint（含 `確認收到還款.feature` 的全部 5 種錯誤情境字面訊息，含金額比對對象已改為 `advancePaymentAmount`）
- [x] Chrome Test Guard 通過 — 本輪環境問題已解除（見下方說明），實際跑過完整互動流程

### 補充：實作細節（本輪修正）

**核心語意修正**：`web/src/app/transactions/pending-advance-payments/page.tsx` 的 `openSettleForm()` 原本
`setSettleAmount(String(t.amount))`（預帶交易總金額），修正為 `setSettleAmount(t.advancePaymentAmount != null ? String(t.advancePaymentAmount) : '')`
（預帶代墊金額）。這是整個修正案最容易做錯的一步——若沿用舊邏輯，使用者在待收回代墊款頁按下「確認收到還款」
會看到表單預填 4000（總金額）而非 3000（代墊金額），實際送出後端會回 422「還款金額與代墊金額不符，僅支援
全額還款」，使用者會一頭霧水。Chrome 實測已確認修正後預填值正確為 3000（見下方 Chrome Test Guard 紀錄）。

**編輯頁修正**：第一輪因為後端 `update_transaction()` 完全不接受代墊款參數，前端刻意用 `showAdvancePayment={false}`
擋掉編輯頁的代墊金額欄位。本輪後端已補上該支援（Phase05 卡片項目 6），故編輯頁移除此限制，並從 URL query
的 `advancePaymentAmount` 參數帶入初始值（`calendar/page.tsx` 的編輯連結同步補上該 query 參數）。

**路由選擇 / 新頁面位置**（沿用第一輪決策，本輪未變更）：`GET /api/transactions/pending-advance-payments` 路徑依 api.yml；`web/src/app/transactions/pending-advance-payments/page.tsx` 歸在 `transactions/` 下，`web/src/app/settings/page.tsx` 提供入口，`BottomNav` 未變動。

**MSW settle-advance-payment 錯誤檢查順序**（沿用第一輪決策，比對對象已修正）：找不到交易(404) → 必要參數未提供(400) → 非代墊款交易(422，判斷條件改為 `advancePaymentAmount == null`) → 已結清(422) → 金額不符(422，比對對象改為 `transaction.advancePaymentAmount`) → 找不到帳戶(404) → 成功建立收入交易並標記原交易已結清。

### Chrome Test Guard 執行紀錄（2026-08-24 22:15，本輪環境已可用）

第一輪卡在 playwright MCP profile 鎖定衝突（`mcp-chrome-75af306` 被另一 process 持有），本輪重試時該衝突已不再出現，
`mcp__playwright__browser_navigate` 正常運作，完整跑過以下流程（`NEXT_PUBLIC_MOCK_API=true npm run dev`，啟動於
`http://localhost:3001`，3000 被其他容器佔用）：

1. 開啟 `/transactions/new`，切到支出、選分類「餐飲」、金額 4000、帳戶「永豐銀行」、代墊金額 3000，送出成功，
   client-side 導向 `/calendar`。
2. `/calendar` 當日列表出現新交易，徽章顯示「代墊款 $3,000 · 待收回」（珊瑚色），本月支出正確累加為 8,000
   （原本 fixture 的 4,000 + 新建立的 4,000，代墊款尚未結清時仍全額計入，符合規格）。
3. 經 設定 → 待收回代墊款（client-side 導覽，MSW 記憶體狀態保留），清單顯示兩筆，皆正確顯示
   「總額 $4,000（代墊 $3,000）」。
4. 點開新建立那筆的「確認收到還款」表單，確認金額欄位**預填 3000**（非 4000）。
5. 故意改成 4000 送出 → 顯示錯誤「還款金額與代墊金額不符，僅支援全額還款」（對應後端 422，console 記錄一筆
   預期中的 422 network log，非程式錯誤）。
6. 改回 3000、選帳戶「永豐銀行」送出 → 成功，該筆從待收回清單消失，僅剩原本 fixture 那筆。
7. 全程 `browser_console_messages(level="error", all=true)` 檢查：整個 session 僅有步驟 5 那筆預期中的 422
   資源載入錯誤，無其他未預期的 console error。
8. 驗證結束後執行 `pkill -f "next dev"` 停止 dev server，確認無殘留 process。

**結論**：核心語意修正（settle 表單預帶代墊金額而非總金額）已透過瀏覽器實測確認正確；全流程（新增混合代墊交易 →
行事曆徽章 → 待收回清單雙金額顯示 → 表單預填 → 金額不符錯誤 → 修正後成功結清 → 從清單消失）皆符合規格預期。
