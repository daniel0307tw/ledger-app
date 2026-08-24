@query
Feature: 報表 — 查詢分類花費明細
  作為 使用者
  我要 查詢某段期間內、某個分類的所有收支紀錄明細列表
  以便 點開報表中的某個分類，看清楚這個分類的錢實際花在哪些交易上

  # specs/features/系統抽象.md, specs/features/reports/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 前置（參數）- 查詢期間必須提供分類、起始日期與結束日期，比照既有「查詢分類花費統計」的慣例

    Scenario Outline: 缺少 <缺少參數> 時操作失敗
      When 使用者查詢分類花費明細，分類 <category> 起始日期 <start_date> 結束日期 <end_date>
      Then 操作失敗，錯誤為"必要參數未提供"

      Examples:
        | 缺少參數 | category | start_date | end_date   |
        | 分類     |          | 2026-08-01 | 2026-08-31 |
        | 起始日期 | 餐飲     |            | 2026-08-31 |
        | 結束日期 | 餐飲     | 2026-08-01 |            |

  Rule: 前置（參數）- 起始日期必須不晚於結束日期，比照既有「查詢分類花費統計」的慣例

    Example: 起始日期晚於結束日期時操作失敗
      When 使用者查詢分類花費明細，分類 餐飲 起始日期 2026-09-01 結束日期 2026-08-01
      Then 操作失敗，錯誤為"起始日期不可晚於結束日期"

  Rule: 後置（回應）- 查詢結果應為期間內屬於該分類的收支紀錄明細列表，依日期新到舊排序，且不含其他分類的紀錄

    Example: 查詢結果應只包含該分類、期間內的明細，依日期新到舊排序，且保留備註內容
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | note   |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 | 晚餐   |
        | 2  | 2026-08-10 | 40     | 餐飲     | 永豐銀行 | 支出 | 牙刷   |
        | 3  | 2026-08-15 | 200    | 交通     | 永豐銀行 | 支出 |        |
      When 使用者查詢分類花費明細，分類 餐飲 起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下收支紀錄明細：
        | date       | category | amount | account  | note   |
        | 2026-08-10 | 餐飲     | 40     | 永豐銀行 | 牙刷   |
        | 2026-08-05 | 餐飲     | 500    | 永豐銀行 | 晚餐   |

  Rule: 後置（回應）- 轉帳紀錄與收入紀錄不列入明細，比照既有「查詢分類花費統計」的加總範圍慣例

    Example: 轉帳與收入產生的紀錄不出現在明細中
      Given 系統中有以下帳戶：
        | name     |
        | 新光銀行 |
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 新光銀行   | 2000   | 2026-08-10 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |
        | 2  | 2026-08-12 | 30000  | 餐飲     | 永豐銀行 | 收入 |
      When 使用者查詢分類花費明細，分類 餐飲 起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下收支紀錄明細：
        | date       | category | amount | account  |
        | 2026-08-05 | 餐飲     | 500    | 永豐銀行 |

  Rule: 後置（回應）- 已結清（advancePaymentStatus=settled）的代墊款交易，明細中顯示交易總金額與代墊款相關欄位；計入本分類期間有效金額加總的部分為「總金額 − 代墊金額」，與既有「查詢分類花費統計」feature 的對應 Rule 完全一致

    Example: 已結清代墊款交易明細顯示總金額，加總結果與分類花費統計一致
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |                        |                        |
        | 2  | 2026-08-10 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled                |
      When 使用者查詢分類花費明細，分類 餐飲 起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下收支紀錄明細：
        | date       | category | amount | account  | advancePaymentAmount | advancePaymentStatus |
        | 2026-08-10 | 餐飲     | 4000   | 永豐銀行 | 3000                   | settled                |
        | 2026-08-05 | 餐飲     | 500    | 永豐銀行 |                        |                        |
      # 有效金額加總 = 500 + (4000-3000) = 1500，對照 tests/features/reports/查詢分類花費統計.feature 同組資料的 Example 結果 1500，一致

  Rule: 後置（回應）- 尚未結清的代墊款交易，明細與加總皆以交易總金額計入，與既有「查詢分類花費統計」feature 的對應 Rule 完全一致

    Example: 未結清代墊款交易以總金額計入加總
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |                        |                        |
        | 2  | 2026-08-10 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者查詢分類花費明細，分類 餐飲 起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下收支紀錄明細：
        | date       | category | amount | account  | advancePaymentAmount | advancePaymentStatus |
        | 2026-08-10 | 餐飲     | 4000   | 永豐銀行 | 3000                   | pending                |
        | 2026-08-05 | 餐飲     | 500    | 永豐銀行 |                        |                        |
      # 有效金額加總 = 500 + 4000 = 4500，對照 tests/features/reports/查詢分類花費統計.feature 同組資料的 Example 結果 4500，一致

  Rule: 後置（回應）- 期間內該分類完全沒有符合條件的交易時，查詢結果為空列表（非錯誤）

    Example: 沒有任何符合條件的交易時查詢結果為空
      When 使用者查詢分類花費明細，分類 餐飲 起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下收支紀錄明細：
        | date | category | amount | account |
