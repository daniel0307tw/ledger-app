# Execution Plan — 接收股票交易現金異動

> 產出於 Phase 01 Discovery，2026-09-16。既有系統（Structural Read：既有 `transactions` domain 的
> `transaction_service.py` / `transfer_service.py` / `cash_sync.py`；「雲端發票同步」domain 提供第三方
> 系統 Actor 呼叫 API 建立交易的既有先例，本輪沿用其模式）。

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 4（1 Activity、3 Feature） |
| Modify | 1（erm.dbml 的 ledger_transaction 表） |
| Delete | 0 |

## 範圍決策摘要（Clarify Loop 已確認）

1. **雙重同步風險**：既有 `sync_to_cash_position()` 由 `TransactionService` 與 `TransferService` 的
   create/update/delete 路徑統一呼叫，寫入 stock_analyzer 的 `cash_position` 表。本輪新增的「接收
   stock_analyzer 推送」路徑**必須是新的、獨立的 service 方法**，且**不呼叫** `sync_to_cash_position()`
   / `cancel_previous_sync()`——因為 stock_analyzer 已經在它自己那邊寫過 `cash_position`，若 ledger-app
   這邊建立交易時又反向同步一次，會造成現金被重複計算。
2. **報表/預算處理**：比照既有 `TransferService` 的 `is_transfer=true` 模式——`category_id=null`，
   不計入一般收支報表與預算。
3. **來源標記**：`ledger_transaction` 新增 `is_stock_sync`（boolean, not null, default false）欄位，
   標記這筆交易是否由 stock_analyzer 推送建立，用途：(a) 建立時判斷跳過反向同步、(b) 更新/刪除時驗證
   目標交易確實是 stock_analyzer 建立的（不可誤更新/刪除使用者手動記的交易）、(c) UI 可用於識別顯示。
4. **關聯鍵**：ledger-app 回傳自己的 `ledger_transaction.id` 給 stock_analyzer 保存；後續更新/刪除請求
   直接帶這個 id 回來，ledger-app 不需要額外儲存 stock_analyzer 端的交易 id。
5. **找不到目標交易**：更新/刪除時找不到對應 id，或該 id 對應的交易 `is_stock_sync=false`，比照既有
   `NotFoundError` 慣例回應「找不到該筆交易」。

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| modify | `ledger_transaction` 表 | 新增 `is_stock_sync` 欄位（boolean, not null, default false） |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `cash-sync` domain 完整句型分析 + Examples | 涵蓋 3 個 Feature：接收股票交易建立記帳交易、接收股票交易更新記帳交易、接收股票交易刪除記帳交易 |

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `POST /api/stock-sync/transactions`（建立） | Request：方向/金額/幣別/帳戶名稱；Response：交易 id |
| create | `PUT /api/stock-sync/transactions/{id}`（更新） | Request：金額/方向 |
| create | `DELETE /api/stock-sync/transactions/{id}`（刪除） | 無 body |

> 確切路徑/schema 由 Phase 04 Reconciler 依 Feature 的 command 正式推導，此處為方向性預告。

## Phase 05-07：本輪不執行

依使用者指示，本輪只做到 Phase 04（External Quality + API 契約），實作、前端、整合驗證留待之後另外指示。
