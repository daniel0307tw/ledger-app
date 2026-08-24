# 工程計畫：ledger-net-worth

> **狀態**: COMPLETED
> **建立日期**: 2026-08-24
> **最後更新**: 2026-08-24
> **技術棧**: python (e2e)
> **需求摘要**: 新增資產/淨值總覽分頁，整合現金帳戶餘額、信用卡負債、與 stock_analyzer 股票市值（唯讀查詢）

---

## Dependency Graph

| Phase | Name | Depends On | 狀態 |
|-------|------|------------|------|
| 01 | Requirement Analysis（需求分析 + 影響評估 + 行為設計） | — | done |
| 02 | Entity Modeling（外部品質 — 資料） | 01 | done |
| 03 | BDD Analysis（外部品質 — 可執行規格） | 02 | done |
| 04 | API Contract（內部品質） | 03 | done |
| 05 | Backend TDD Track | 04 | done |
| 06 | Frontend Build Track | 04 | done |
| 07 | Integration Validation | 05, 06 | done |

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
| Execution Plan | `plans/ledger-net-worth/plan.md` | Phase 02-07（scope 依據） |
| Activity Diagrams | `specs/activities/` | Phase 06（Chrome Test Guard 測試計畫結構） |
| Feature Files（含 Examples） | `tests/features/` | Phase 05（TDD 循環） |
| erm.dbml | `specs/erm.dbml` | Phase 05（Schema Analysis） |
| api.yml | `specs/api.yml` | Phase 05（Red 欄位守衛）、Phase 06（MSW handlers）、Phase 07（驗證基準） |

## Execution Plan（Phase 01 產出）

### 概覽

| 類型 | 數量 |
|------|------|
| Create | 5 |
| Modify | 1 |
| Delete | 0 |

### Phase 02: Entity Modeling

無操作。股票資料為外部系統 stock_analyzer 既有表（唯讀反射，不 import 對方 schema 進本專案 erm.dbml）；現金/信用卡沿用既有 `account.balance` 計算邏輯。`specs/erm.dbml` 不變。

### Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `assets/` domain（查詢資產總覽.feature） | 全新 query domain，需完整分析（系統抽象 + 句型模型 + Examples） |

### Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `GET /api/net-worth`（暫定路徑，Phase 04 依專案慣例確認） | 新增唯讀查詢 endpoint，彙整現金/信用卡/股票三項 |

### 外部依賴前置工作（不在 ledger-app 的 Phase 05-07 範圍內，由我直接於 stock_analyzer 專案實作）

Clarify Loop 發現 `tw_holding`/`us_holding` 表從未被寫入，實際的持倉／市值／損益是 stock_analyzer 既有的 `journal_service.get_portfolio_overview(market)`（FIFO 沖銷 + `journal_price_snapshot` 即時價快取）即時算出來的，重新在 ledger-app 實作一次同樣的 FIFO/XIRR 邏輯風險過高（複雜、易與正本兜不起來）。

**決策（使用者已確認）**：在 stock_analyzer 新增一個最小的唯讀 API（例如 `GET /api/portfolio/holdings?market=tw|us`，回傳 `get_portfolio_overview()` 已算好的個股明細 + 市值），直接複用既有計算邏輯，不重寫。此 API 只回傳股票資料，不含現金（現金/信用卡負債完全是 ledger-app 自己的概念）。

| 操作 | 目標 | 說明 | 狀態 |
|------|------|------|------|
| create | `/home/daniel/stock_analyzer/app/api_server.py` | Starlette（非 FastAPI，避免新增依賴）唯讀 API `GET /api/portfolio/holdings?market=tw\|us`，直接呼叫既有 `JournalService.get_portfolio_overview()`，不重寫任何計算邏輯 | **DONE** — 已啟動於 `http://127.0.0.1:8100`，curl 驗證回傳 TWD 市值 356314.05，與使用者稍早在 stock_analyzer 畫面上看到的數字完全一致；`run_api_server.sh` 供之後重啟 |

### Phase 05-07: Implementation（ledger-app 範圍）

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `app/repositories/holding_repository.py` | 呼叫 stock_analyzer 新增的唯讀 API（HTTP client），**不再**直接反射 tw_holding/us_holding（已確認該表未使用） |
| create | `app/services/net_worth_service.py`（或等效） | 彙整現金/信用卡（既有 AccountService）+ 股票市值（新 HoldingRepository，經 HTTP 取得） |
| create | `app/api/net_worth.py`（或等效） | 新 endpoint，回傳分幣別（TWD/USD）小計，不做匯率換算 |
| create | 前端 `web/src/app/assets/page.tsx` | 新分頁，列個股明細（symbol/name/市值/損益）+ 現金/信用卡總額 |
| modify | `web/src/components/BottomNav.tsx` | 三分頁 → 四分頁，新增「資產」 |
| red-green-refactor | `assets/查詢資產總覽.feature` | 新 feature 的 TDD |

### IMPL_IMPACT（由 Phase 02-04 Reconciler 回填）

| Phase | 影響目標 | Impact Type | 來源 | 說明 |
|-------|---------|-------------|------|------|
| 05 | `app/repositories/holding_repository.py` | `NEW_OPERATION` | Phase 01 | 新 Repository，HTTP client 呼叫 stock_analyzer 新 API（非 SQLite 反射） |
| 05 | `app/core/config.py` | `NEW_OPERATION` | Phase 01 | 新增 `STOCK_ANALYZER_API_BASE_URL` 設定 |
| 06 | `mocks/handlers/`、`src/app/assets/` | `NEW_OPERATION` | Phase 04 | 新 endpoint 對應的 MSW handler + 頁面 |
| 06 | `src/components/BottomNav.tsx` | `ENDPOINT_SCHEMA`（UI 層） | Phase 01 | 新增第四個分頁 |
| 07 | test-plans/ | — | Phase 01 | 新流程需要新增測試計畫結構 |
| — | stock_analyzer 新 API | 外部前置依賴 | Phase 01 | Phase 05 開始前必須先完成，否則 HoldingRepository 無可呼叫對象 |
| 05 | Step Defs（`tests/features/steps/assets_steps.py`，新檔） | `NEW_OPERATION` | Phase 03 | 8 個 Scenario，5 個新句型（G3/G4/G5/T2/T3/T4/T5，W1）需要新 Step Def；G1/G2 沿用既有 |
| 05 | `app/services/net_worth_service.py` 回傳格式 | `NEW_OPERATION` | Phase 03 | 需回傳 cash_total/credit_card_debt_total/股票個股明細列表/幣別小計列表四類資料 |

### Phase 03 補充：外部系統 Step Def 實作提示（供 Phase 05 參考）

G3/G4/G5 對應「stock_analyzer 唯讀 API」的測試替身，**不是**本地資料庫寫入。Phase 05 撰寫 Step Def 時，`HoldingRepository`（呼叫 stock_analyzer HTTP API）需要可被測試替身（mock/monkeypatch HTTP client）介入，比照既有 `CashPositionRepository` 的 `set_cash_position_db_path()` 測試覆寫模式，設計等效的 `set_stock_analyzer_api_base_url()` 或注入測試用 HTTP client。

### Clarify Loop 已確認事項（Step 6）

1. **幣別**：TWD/USD 分開顯示小計，不做匯率換算（與 stock_analyzer 自己的既有決策一致）
2. **頁面呈現**：股票列個股明細；現金/信用卡顯示總額（不逐帳戶列）
3. **journal 範圍**：交由 stock_analyzer 既有邏輯處理，ledger-app 不需關心（已改為呼叫既有 API，非直接查表）
4. **資料即時性**：每次進頁即時查詢，不快取
5. **錯誤處理**：stock_analyzer API 查詢失敗時，現金/信用卡正常顯示，股票部分顯示錯誤提示（partial failure，非整頁失敗）
6. **空持股**：顯示 $0 + 提示文字（目前非空狀態，但保留此行為以防未來持股歸零）

## Context Management

- 三層持久化：檔案系統（卡片）+ TodoWrite + Context Window
- Compact Proof 層次化：specformula 16 任務 / 各 Phase 內部自管細節
- Lazy Loading：每個 Phase 只載入當前 skill，跨 skill 必定重新 LOAD
- 詳見 skill `references/context-management.md`
