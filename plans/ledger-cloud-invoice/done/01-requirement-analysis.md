# Phase 01: Requirement Analysis（需求分析 + 影響評估 + 行為設計）

## 審查進度

- [x] 01.1 相關規格已審查 — **簽名**: 2026-08-24 14:10
- [x] 01.2 交付物已審查 — **簽名**: 2026-08-24 14:10

## 自我審查備註（「go unti need Clarify」自動模式）

範圍在 Clarify Loop 中從單一「雲端發票同步」擴大為 4 個子功能（使用者明確要求「這輪全部一起做」）。
共兩輪 AskUserQuestion（scope 確認 + 8 項細節決策）+ 1 輪 3 題（未來交易統計/補生成觸發/健康狀態口徑），
全部記錄於 `specs/clarify/2026-08-24-1400.md`。認證機制一項由查證既有程式碼自行解決，未詢問使用者。
Quality Gate 三項檢查（Actor 合法性、CiC 歸零、Execution Plan 完整）均通過，詳見下方驗收點。

## 目的 (What)

理解需求意圖，評估對現有系統的影響，設計行為結構（Activity + Feature Rules）。

**統一流程** — 不區分 greenfield / 新功能 / 改變需求。三者是同一件事，差別只在起始狀態：

| 情境 | 起始狀態 | Delta |
|------|---------|-------|
| Greenfield | 空 | 全部 create |
| 新功能（既有系統） | 已有 artifacts | create + 可能 modify |
| 改變需求 | 已有 artifacts | modify + 可能 create/delete |

**每個需求都是 current state → desired state 的 delta 操作。**

觸發 skill：`/aibdd-discovery`

## 統一流程（6 步）

### Step 1: Composition Analysis
理解需求意圖。DELEGATE `/aibdd-composition-analysis`。
- 產出：組成盤點表 + 完整度評估

### Step 2: Structural Read
掃描現有 artifacts（`specs` 下的 activities、features、entity、api）。
- **Greenfield**：回傳空集，快速通過
- **既有系統**：建立 dependency graph — 哪些 artifact 存在、彼此如何關聯

### Step 3: Impact Analysis
計算 delta：需求意圖 vs 現有狀態 → 哪些 artifacts 需要 create / modify / delete。
- 產出：**Execution Plan**（見下方格式）
- Execution Plan 是 Phase 02-08 的 scope 依據
- **Greenfield**：Execution Plan = "create all"（退化情況）

### Step 4: Clarify & Resolve
處理衝突和模稜兩可。澄清循環（CiC 便條紙歸零）。
- 新增的部分：CiC 標記未確認之處
- 修改的部分：確認修改意圖不與現有 Rules 矛盾
- 刪除的部分：確認刪除不會破壞上下游依賴

### Step 5: Behavior Design
依 Execution Plan 產出行為結構：
- **create**：新建 Activity Diagram + Feature Files（Rules only，無 Examples）
- **modify**：修改現有 Activity / Feature 的 Rules
- **delete**：移除不再需要的 Activity / Feature
- 品質掃描：Actor 合法性 + 面向覆蓋率 F1-F6

### Step 6: Quality Gate
- CiC 便條紙歸零
- Actor 合法性通過
- F1-F6 覆蓋率 Clear
- Execution Plan 中所有 behavior 操作完成

## Execution Plan 格式

Phase 01 的核心產出。儲存於 `plans/ledger-cloud-invoice/plan.md`。

```markdown
# Execution Plan

## 概覽
| 類型 | 數量 |
|------|------|
| Create | N |
| Modify | M |
| Delete | K |

## Phase 02: Entity Modeling
| 操作 | 目標 | 說明 |
|------|------|------|
| create | Lead table | 新增實體 |
| modify | Journey table | 加 stage 欄位 |

## Phase 03: BDD Analysis
| 操作 | 目標 | 說明 |
|------|------|------|
| create | lead/ domain | 全新 domain，需完整分析 |
| modify | journey/句型.md | 新增 stage 相關句型 |

## Phase 04: API Contract
| 操作 | 目標 | 說明 |
|------|------|------|
| create | POST /api/leads | 新增 endpoint |
| modify | GET /api/journeys | 加 stage filter param |

## Phase 05-08: Implementation
| 操作 | 目標 | 說明 |
|------|------|------|
| red-green-refactor | lead/*.feature | 新 feature 的 TDD |
| red-green-refactor | journey/Journey流程.feature | 修改的 feature 重跑 TDD |

## IMPL_IMPACT（由 Phase 02-04 Reconciler 回填）
| Phase | 影響目標 | Impact Type | 來源 | 說明 |
|-------|---------|-------------|------|------|
| 05 | step_defs/lead_steps | DATATABLE_SCHEMA | Phase 03 | Given datatable +source column |
| 05 | models/lead | FIELD_CHANGE | Phase 02 | +source:varchar |
| 05 | migrations/ | FIELD_CHANGE | Phase 02 | Lead table +source column |
| 06 | mocks/handlers/ | ENDPOINT_SCHEMA | Phase 04 | GET /leads response +source |
| 06 | pages/lead/ | ENDPOINT_SCHEMA | Phase 04 | Lead 列表顯示 +source |
| 07 | test-plans/ | — | Phase 01 | Activity 結構變更時重新產出 |
| 08 | — | — | auto | Phase 05 或 06 有影響 → 重跑整合驗證 |
```

**Phase 02-08 讀取 Execution Plan 決定自己的工作範圍。** 若某 Phase 在 Execution Plan 中無操作，carry-on 可快速通過（仍需使用者 LGTM）。

**IMPL_IMPACT 傳播機制**：
- Phase 01 產出初始 Execution Plan（Phase 05-08 的 scope = `NEW_OPERATION` 或空）
- Phase 02-04 各自的 Reconciler 完成後，將 change_summary 中的 IMPL_IMPACT 回填到 Execution Plan
- Phase 05-08 啟動時讀取已回填的 IMPL_IMPACT，決定走 **one-shot**（正常 TDD）或 **targeted fix**（定向修復）

## 相關規格

| # | 規格 | 路徑 | 說明 |
|---|------|------|------|
| 1 | 組成盤點表 | Discovery 內部產出 | 需求完整度評估 |
| 2 | Execution Plan | `plans/ledger-cloud-invoice/plan.md` | 跨 Phase 的 scope 依據 |

## 交付物

carry-on Step 01.2 觸發時：

1. **DELEGATE `/aibdd-discovery`**，傳入需求描述 + `specs`
2. Discovery 執行統一流程（6 步）：
   - Composition Analysis → Structural Read → Impact Analysis
   - → Clarify & Resolve（CiC 歸零）
   - → Behavior Design（create/modify/delete activities + features）
   - → Quality Gate（Actor + Coverage）
3. 產出 Execution Plan → 寫入 `plans/ledger-cloud-invoice/plan.md`
4. Discovery 完成後回傳控制權

| # | 交付物 | 路徑 | 狀態 |
|---|--------|------|------|
| 01.1 | Execution Plan | `plans/ledger-cloud-invoice/plan.md` | DONE |
| 01.2 | Activity Diagrams（4 個） | `specs/activities/{雲端發票同步,雲端發票待確認處理,固定收支管理,預算編列}.mmd` | DONE |
| 01.3 | Feature Files（Rules only，14 個） | `tests/features/{cloud-invoices,recurring-transactions,budgets}/*.feature` | DONE |
| 01.4 | Actor 定義 | `specs/actors/Hermes.md`（新增）、`specs/actors/使用者.md`（既有，沿用） | DONE |
| 01.5 | 澄清紀錄 | `specs/clarify/2026-08-24-1400.md` | DONE |

### 驗收點

- [x] Composition Analysis 完成
- [x] Structural Read 完成（既有系統）
- [x] Execution Plan 產出，涵蓋 Phase 02-08 的 scope
- [x] Grep `CiC\(` 掃描 `activities/` + `features/` 結果為空
- [x] Actor 合法性掃描通過（使用者、Hermes 均為合法外部 Actor）
- [x] 面向覆蓋率自我檢視（各 domain 的 CRUD/query 完整度已對照 Execution Plan 逐一核對）
- [x] 所有新建 .feature 含 Rules、標記 `@ignore`、無 Examples
