# Execution Plan — ledger-report-category-drilldown

## 概覽

| 類型 | 數量 |
|------|------|
| Create | 2 |
| Modify | 2 |

## Change Composition 摘要

新增一個查詢功能：「查詢分類花費明細」——報表頁面點開某個分類，看到該分類、該期間內的收支紀錄明細列表。有效金額計算邏輯（已結清代墊款計「總金額－代墊金額」）直接引用既有「查詢分類花費統計」feature 的對應 Rule，非新設計。排序沿用既有 `transaction_repository.py` 的 `date desc, id desc` 慣例；無分頁設計（比照既有交易列表查詢，本系統目前所有列表查詢均無分頁）。

## Phase 02: Entity Modeling

| 操作 | 目標 | 說明 |
|------|------|------|
| none | `specs/erm.dbml` | 不需異動。新 query 完全基於 `ledger_transaction` 既有欄位（含代墊款欄位），無新增表/欄位 |

## Phase 03: BDD Analysis

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `tests/features/reports/查詢分類花費明細.feature` | 全新 query，7 個 Rule 待補 Example（本輪 Phase 01 已建立 Rules-only 骨架） |

## Phase 04: API Contract

| 操作 | 目標 | 說明 |
|------|------|------|
| create | `GET /api/reports/category-detail` | 查詢參數：`category`（必填）、`startDate`（必填）、`endDate`（必填）；回傳交易明細陣列，欄位含 date/amount/note/account/type/advancePaymentAmount/advancePaymentStatus |

## Phase 05-07: Implementation

| 操作 | 目標 | 說明 |
|------|------|------|
| one-shot TDD | `tests/features/reports/查詢分類花費明細.feature` | 全新 endpoint，依標準 TDD 循環實作；有效金額計算直接複用 `app/repositories/transaction_repository.py` 既有的 `_effective_amount()` CASE 表達式 |
| frontend | `web/src/app/reports/page.tsx` | 點擊分類（圓餅圖 or 圖例）→ 展開/導頁顯示明細列表；UI 呈現方式由 Phase 06 依現有 UI 慣例決定 |

## 已確認的設計決策（可直接用於後續 Phase，不需要再問使用者）

1. 有效金額計算邏輯 = 既有「查詢分類花費統計」feature 對應 Rule 的直接引用（settled 代墊款計總金額－代墊金額，pending 仍計總金額全額）
2. 排序：date desc, id desc（比照 `transaction_repository.py` 既有交易列表查詢慣例）
3. 不分頁（比照本系統所有既有列表查詢，目前均無分頁機制）
4. 過濾範圍：排除轉帳與收入紀錄（比照既有「查詢分類花費統計」的加總範圍）
5. 期間內無符合條件交易 → 回傳空列表，非錯誤（比照既有「查詢分類花費統計」的對應 Rule）
6. erm.dbml 不需異動，確認 Phase 01 分析假設成立
7. 明細卡片版面（Phase 06 前端呈現，使用者明確指定）：上排顯示「分類、時間、備註、金額」；「支付方式」（即 account 欄位）寫在金額正下方，不是獨立跨版面的下排

## Structural Read 摘要

- 最相近既有 feature：`tests/features/reports/查詢分類花費統計.feature`（Background 帳戶慣例、參數驗證 Rule、代墊款有效金額 Rule 均直接沿用）
- 既有 Activity：`specs/activities/分類花費報表.mmd`（已 modify，新增 STEP:2 分支）
- 既有前端：`web/src/app/reports/page.tsx`（顯示 `CategoryPieChart`，尚無點擊互動）
- erm.dbml／api.yml：`ledger_transaction` 表既有欄位已涵蓋所需資料，本次僅需新增一個 endpoint schema
