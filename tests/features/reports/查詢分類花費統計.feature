@query
Feature: 報表 — 查詢分類花費統計
  作為 使用者
  我要 查詢某段期間內依分類分組的支出統計
  以便 用圖表檢視這段期間的花費都花在哪些分類

  # specs/features/系統抽象.md, specs/features/reports/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 前置（參數）- 查詢期間必須提供起始日期與結束日期，比照既有收支紀錄查詢的慣例

    Scenario Outline: 缺少 <缺少參數> 時操作失敗
      When 使用者查詢分類花費統計，起始日期 <start_date> 結束日期 <end_date>
      Then 操作失敗，錯誤為"必要參數未提供"

      Examples:
        | 缺少參數 | start_date | end_date   |
        | 起始日期 |            | 2026-08-31 |
        | 結束日期 | 2026-08-01 |            |

  Rule: 前置（參數）- 起始日期必須不晚於結束日期，比照既有收支紀錄查詢的慣例

    Example: 起始日期晚於結束日期時操作失敗
      When 使用者查詢分類花費統計，起始日期 2026-09-01 結束日期 2026-08-01
      Then 操作失敗，錯誤為"起始日期不可晚於結束日期"

  Rule: 後置（回應）- 查詢結果應為期間內依分類分組的支出金額加總，且排除轉帳紀錄與收入紀錄

    Example: 查詢結果應依分類正確分組加總金額
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |
        | 2  | 2026-08-10 | 300    | 餐飲     | 永豐銀行 | 支出 |
        | 3  | 2026-08-15 | 200    | 交通     | 永豐銀行 | 支出 |
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
        | 餐飲     | 800          |
        | 交通     | 200          |

    Example: 轉帳產生的紀錄不計入分類花費統計
      Given 系統中有以下帳戶：
        | name     |
        | 新光銀行 |
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 新光銀行   | 2000   | 2026-08-10 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
        | 餐飲     | 500          |

    Example: 收入紀錄不計入分類花費統計
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |
        | 2  | 2026-08-15 | 30000  | 餐飲     | 永豐銀行 | 收入 |
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
        | 餐飲     | 500          |

  Rule: 後置（回應）- 期間內完全沒有花費的分類不應出現在統計結果中

    Example: 期間外的紀錄所屬分類不出現在結果中
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |
        | 2  | 2026-07-20 | 200    | 交通     | 永豐銀行 | 支出 |
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
        | 餐飲     | 500          |

  Rule: 後置（回應）- 已結清（advancePaymentStatus=settled）的代墊款交易，計入分類花費統計的有效金額為「總金額 − 代墊金額」；尚未結清的代墊款交易仍以交易總金額計入

    Example: 已結清的代墊款交易只計入總金額扣除代墊金額後的部分
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |                        |                        |
        | 2  | 2026-08-10 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled                |
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
        | 餐飲     | 1500         |

    Example: 尚未結清的代墊款交易仍以交易總金額計入分類花費統計
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 500    | 餐飲     | 永豐銀行 | 支出 |                        |                        |
        | 2  | 2026-08-10 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
        | 餐飲     | 4500         |

  Rule: 後置（回應）- 期間內完全沒有支出紀錄時，查詢結果為空

    Example: 期間內無任何支出紀錄時查詢結果為空
      When 使用者查詢分類花費統計，起始日期 2026-08-01 結束日期 2026-08-31
      Then 操作成功，查詢結果應包含以下分類花費統計：
        | category | total_amount |
