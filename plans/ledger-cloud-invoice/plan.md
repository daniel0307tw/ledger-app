# 工程計畫：ledger-cloud-invoice

> **狀態**: COMPLETED
> **建立日期**: 2026-08-24
> **最後更新**: 2026-08-24
> **技術棧**: python (e2e)
> **需求摘要**: 雲端發票自動同步記帳：新增接收 Hermes 端已抓取結構化發票資料的 API，用發票字軌號碼精確去重，必要時自動記帳；瀏覽器自動化本身不在這輪範圍

---

## Dependency Graph

| Phase | Name | Depends On | 狀態 |
|-------|------|------------|------|
| 01 | Requirement Analysis（需求分析 + 影響評估 + 行為設計） | — | todo |
| 02 | Entity Modeling（外部品質 — 資料） | 01 | todo |
| 03 | BDD Analysis（外部品質 — 可執行規格） | 02 | todo |
| 04 | API Contract（內部品質） | 03 | todo |
| 05 | Backend TDD Track | 04 | todo |
| 06 | Frontend Build Track | 04 | todo |
| 07 | Integration Validation | 05, 06 | todo |

```
01 → 02 → 03 → 04 ──┬──→ 05 ──┐
                     │         │
                     └──→ 06 ──→ 07
                                ↑
                         05 ────┘
```

## 線性執行順序（建議）

> 若無平行資源，依此順序逐一執行。

1. 01-requirement-analysis
2. 02-entity
3. 03-bdd-analysis
4. 04-api-contract
5. 05-backend-tdd
6. 06-frontend-build
7. 07-integration

## 品質框架

### Phase 01: Requirement Analysis（統一入口）

不區分 greenfield / 新功能 / 改變需求。每個需求都是 current state → desired state 的 delta。
Phase 01 產出 **Execution Plan**，決定 Phase 02-07 各自的工作範圍。

### External Quality（外部品質）— Phase 02~04

推理順序：**行為(01) → 資料(02) → 規格精煉(03) → 實作契約(04)**。

| Phase | 推理依據 |
|-------|---------|
| 01 → 02 | 有了行為（features）才能推導「作用在什麼實體上」 |
| 02 → 03 | 有了實體結構（erm.dbml）才能寫出精準的 Examples |
| 03 → 04 | 每個 command/query 天然對應一個 API endpoint |

### Implementation — Phase 05~07

Phase 01-04 的產出物是所有實作 Phase 的共同契約。

## 共同契約

Phase 01-04 的產出物是 Phase 05-07 的共同依據（Single Source of Truth）：

| 產物 | 路徑 | 消費者 |
|------|------|--------|
| Execution Plan | `plans/ledger-cloud-invoice/plan.md` | Phase 02-07（scope 依據） |
| Activity Diagrams | `specs/activities/` | Phase 06（Chrome Test Guard 測試計畫結構） |
| Feature Files（含 Examples） | `tests/features/` | Phase 05（TDD 循環） |
| erm.dbml | `specs/erm.dbml` | Phase 05（Schema Analysis） |
| api.yml | `specs/api.yml` | Phase 05（Red 欄位守衛）、Phase 06（MSW handlers）、Phase 07（驗證基準） |

## Execution Plan（Phase 01 產出，已於 Clarify Loop 擴大範圍——見下方變更記錄）

> **範圍變更記錄**：原始需求只涵蓋「雲端發票同步」，Clarify Loop Q1 使用者要求新增「設定」分頁，
> 並在該分頁內一次做好 4 個子功能：固定收支管理（含提前生成）、編列預算、雲端發票待確認/健康狀態、
> 轉帳入口（既有功能，僅 UI 重新配置）。使用者已明確選擇「這輪全部一起做」（非分輪），故 Execution
> Plan 據此擴大，不是我自行擴大範圍。

### 概覽

| 類型 | 數量 |
|------|------|
| Create | 4 張新表 + 3 個新 domain + 多個新 endpoint + 1 個新前端分頁（含 4 個子頁） |
| Modify | 0（既有 account/category/ledger_transaction/轉帳 不動，轉帳只變 UI 入口位置） |
| Delete | 0 |

### Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `cloud_invoice` table | 記錄已同步/待確認的雲端發票（發票字軌+號碼 unique、日期、金額、賣方、品項摘要、對應 transaction_id nullable、status enum：synced/pending_review/skipped） |
| create | `recurring_transaction` table | 固定收支規則（頻率 enum：每天/每週/每月/每季/每年/每三年、金額、分類、帳戶、類型、開始日期、生成期數、狀態：啟用/停用） |
| create | `budget` table | 預算（範圍 enum：總預算/分類預算、分類 id nullable（總預算時為 null）、月度金額上限） |
| — | 健康狀態 | 由 `cloud_invoice` 表聚合查詢（最後成功時間、失敗次數），不需要獨立表 |

### Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `cloud-invoices/` domain | 同步雲端發票（batch command）+ 查詢待確認清單（query）+ 確認/略過待確認發票（command）+ 查詢同步健康狀態（query） |
| create | `recurring-transactions/` domain | 建立/編輯/刪除/查詢固定收支規則（command+query）+ 系統自動生成到期交易（command，由既有排程或使用者觸發，待細節） |
| create | `budgets/` domain | 建立/編輯/查詢預算（command+query）+ 查詢預算執行狀況（query，比對 ledger_transaction 實際支出） |

### Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `POST /api/cloud-invoices/sync` | 批次同步 |
| create | `GET /api/cloud-invoices/pending`、`POST /api/cloud-invoices/{id}/confirm`、`POST /api/cloud-invoices/{id}/skip` | 待確認清單 + 確認/略過 |
| create | `GET /api/cloud-invoices/health` | 健康狀態（最後成功時間、失敗次數） |
| create | `POST/PUT/DELETE/GET /api/recurring-transactions` | 固定收支 CRUD |
| create | `POST /api/recurring-transactions/{id}/generate`（暫定） | 觸發生成到期交易 |
| create | `POST/PUT/GET /api/budgets`、`GET /api/budgets/status` | 預算 CRUD + 執行狀況查詢 |

### Phase 05-07: Implementation

| 操作 | 目標 | 說明 |
|------|------|------|
| red-green-refactor | 上述 3 個 domain 的 `*.feature` | 新 feature 的 TDD |
| create | 前端「設定」分頁（底部導覽新增第五個分頁） | 4 個子頁：基本設定（含轉帳入口）、固定收支管理、預算編列、雲端發票（待確認清單+健康狀態） |

### 已確認的關鍵決策（Clarify Loop）

1. 雲端發票疑似重複：Hermes 對話詢問 **與** ledger-app 待確認佇列**兩者皆要**（不是二選一）
2. 同步健康狀態：ledger-app 記錄並提供查詢 endpoint（不是完全由 Hermes 自己記）
3. 發票品項明細：只存表頭摘要（比照 receipt-auto-ledger 的 note 慣例），不建品項明細表
4. 固定收支頻率：每天/每週/每月/每季/每年/每三年（固定 6 種選項的 enum，非自由天數）
5. 提前生成：真的預先建立未來 N 筆 `ledger_transaction`（N 由使用者建立規則時指定期數）
6. 預算維度：總預算 + 各分類預算並存（不是二選一）
7. 預算超支：只在網頁視覺顯示，不接 Hermes 主動推播通知
8. 認證機制：既有系統無認證，新 endpoint 比照既有慣例不加

### 待 BDD Analysis / Clarify Loop 進一步釐清的細節（尚未解決）

1. 刪除/停用固定收支規則時，已生成的未來交易保留還是一併刪除？（傾向 ASM：保留，因已是真實交易）
2. 預算週期是否固定為「每月」（未提及季度/年度預算，比照既有分類花費統計報表以月為單位，傾向 ASM：僅月度）
3. 「提前生成」的觸發時機：使用者建立規則當下就生成 N 筆，還是需要另外觸發？
4. 雲端發票待確認/固定收支/預算三個子頁的欄位/操作細節（BDD Analysis 階段依 erm.dbml 展開時處理）

## Context Management

- 三層持久化：檔案系統（卡片）+ TodoWrite + Context Window
- Compact Proof 層次化：specformula 16 任務 / 各 Phase 內部自管細節
- Lazy Loading：每個 Phase 只載入當前 skill，跨 skill 必定重新 LOAD
- 詳見 skill `references/context-management.md`

## IMPL_IMPACT（Phase 02 回填）

| Phase | 影響目標 | Impact Type | 來源 | 說明 |
|-------|---------|-------------|------|------|
| 05 | `ledger_transaction` model/migration | `FIELD_CHANGE` | Phase 02 | +`source_recurring_transaction_id`（nullable FK，非 Execution Plan 原定範圍，Reconciler 依「補生成」Rule 的實際需求推導新增，已於 Phase 02 交付物中說明理由） |
| 05 | `cloud_invoice`（新表） | `NEW_OPERATION` | Phase 02 | 完整 TDD |
| 05 | `recurring_transaction`（新表） | `NEW_OPERATION` | Phase 02 | 完整 TDD |
| 05 | `budget`（新表） | `NEW_OPERATION` | Phase 02 | 完整 TDD |
| 05 | Step Defs（3 個新 domain，14 個 Feature，27 個 Scenario） | `NEW_OPERATION` | Phase 03 | 全新句型，需要完整 Step Def（含批次結果驗證、差量計算驗證、相對日期"(本月)"解析等新 Handler 模式） |
| 05 | 10 個新 endpoint（`app/api/cloud_invoices.py`、`recurring_transactions.py`、`budgets.py` 或等效） | `NEW_OPERATION` | Phase 04 | 完整 TDD（原先擔心 `/api/budgets/status` 會被 `/api/budgets/{id}` 攔截，複查後確認不成立：{id} 路由只掛在 PUT/DELETE，GET 只有 `/budgets` 與 `/budgets/status` 兩個 path，方法不同不會衝突，已移除該則不成立的註解） |
| 06 | 前端「設定」分頁 + 4 個子頁 | `NEW_OPERATION` | Phase 01 Execution Plan | 新增底部導覽第五分頁；MSW handlers 需覆蓋 10 個新 endpoint |
