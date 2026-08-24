# Execution Plan

需求：個人記帳 MVP（快速記帳、行事曆檢視、多帳戶轉帳、股票現金部位同步）
起始狀態：Greenfield（specs 目錄原為空）

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 7 |
| Modify | 0 |
| Delete | 0 |

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| create | transaction（收支紀錄） | 欄位：日期、金額、分類、備註、帳戶、類型（收入/支出）、同步狀態（pending/synced/failed） |
| create | account（帳戶） | 欄位：帳戶名稱（自訂字串，不強制唯一） |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| create | transactions domain | 4 個 Feature：新增/編輯/刪除/查詢收支紀錄，需補上 Examples |
| create | accounts domain | 3 個 Feature：建立帳戶、查詢帳戶列表、帳戶間轉帳，需補上 Examples |

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| create | POST /api/transactions | 新增收支紀錄 |
| create | PUT /api/transactions/{id} | 編輯收支紀錄 |
| create | DELETE /api/transactions/{id} | 刪除收支紀錄 |
| create | GET /api/transactions | 查詢收支紀錄（依日期區間） |
| create | POST /api/accounts | 建立帳戶 |
| create | GET /api/accounts | 查詢帳戶列表 |
| create | POST /api/transfers | 帳戶間轉帳 |

## Phase 05-07: Implementation

| 操作 | 目標 | 說明 |
|------|------|------|
| red-green-refactor | transactions/*.feature | 4 個 Feature 的 TDD，含 CashPosition 同步邏輯（直接讀寫 stock_analyzer 的 /home/daniel/stock_analyzer/data/stock_analyzer.db） |
| red-green-refactor | accounts/*.feature | 3 個 Feature 的 TDD |
| frontend | web/ | PWA 頁面：記帳快速輸入、行事曆檢視、帳戶列表、轉帳 |
| integration | — | 前後端真實連線驗證 |

## 本輪 Discovery 已確認的關鍵決策（供後續 Phase 直接引用，不需重新澄清）

1. **CashPosition 整合方式**：ledger-app 後端直接讀寫 stock_analyzer 同一個 SQLite 檔案（`/home/daniel/stock_analyzer/data/stock_analyzer.db`），不 import 對方程式碼、不改對方 schema。
2. **收入/支出方向**：交易新增獨立「類型」欄位（收入/支出），金額一律正數。
3. **同步失敗處理**：交易本身照常成功，標記為 pending，重試機制細節留給 Phase 05 決定。
4. **編輯/刪除已同步或待重試的交易**：一律取消舊的待重試任務，依最新內容重新嘗試一次同步（或依刪除而不再嘗試）。
5. **帳戶餘額**：本輪不維護餘額概念，轉帳/支出前不做餘額檢查。
6. **帳戶類型**：使用者自訂名稱，不限定類型清單，不強制唯一。
7. **行事曆檢視**：與「查詢收支紀錄」共用同一個 GET 端點，前端以月曆呈現；可直接點日期/紀錄進入新增或編輯。

## IMPL_IMPACT

Greenfield，所有 Phase 05-07 的 scope 皆為 `NEW_OPERATION`，走 One-shot TDD / One-shot Build，不需 Targeted Fix。
