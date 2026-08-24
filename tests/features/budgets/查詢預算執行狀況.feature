@query
Feature: 查詢預算執行狀況

  Background:
    Given 系統中有以下帳戶：
      | id | name | type   |
      | 1  | 現金 | 一般帳戶 |
    Given 系統中有以下預算：
      | id | scope    | category | monthly_amount |
      | 1  | 分類預算 | 餐飲     | 8000            |

  Rule: 前置（參數）- 查詢範圍為當月（本月 1 號至今），不支援查詢歷史月份  # 設計依據：使用者只提到「編列預算」與網頁視覺顯示，未提及歷史月份回顧需求，且既有分類花費統計報表已可查歷史區間，預算執行狀況聚焦「本月還剩多少額度」的即時性用途

  Rule: 後置（回應）- 查詢結果應包含每個有設定預算的分類（及總預算，如果有設定）的：上限金額、本月已花費金額、剩餘金額、是否已超支

    Example: 本月花費未達上限
      Given 系統中有以下收支紀錄（本月內）：
        | date         | amount | category | account | type |
        | (本月) | 3000   | 餐飲     | 現金    | 支出 |
      When 使用者查詢預算執行狀況
      Then 操作成功，執行狀況應包含：
        | category | monthly_amount | spent | remaining | is_over_budget |
        | 餐飲     | 8000            | 3000  | 5000      | false           |

    Example: 本月花費超過上限
      Given 系統中有以下收支紀錄（本月內）：
        | date         | amount | category | account | type |
        | (本月) | 9000   | 餐飲     | 現金    | 支出 |
      When 使用者查詢預算執行狀況
      Then 操作成功，執行狀況應包含：
        | category | monthly_amount | spent | remaining | is_over_budget |
        | 餐飲     | 8000            | 9000  | -1000     | true            |

    Example: 本月尚無任何花費
      Given 系統中無本月收支紀錄
      When 使用者查詢預算執行狀況
      Then 操作成功，執行狀況應包含：
        | category | monthly_amount | spent | remaining | is_over_budget |
        | 餐飲     | 8000            | 0     | 8000      | false           |

  Rule: 後置（回應）- 轉帳產生的交易（is_transfer=true）不計入預算花費統計，比照既有分類花費統計報表的既定慣例

    Example: 轉帳交易不計入花費統計
      Given 系統中有以下收支紀錄（本月內）：
        | date         | amount | category | account | type | is_transfer |
        | (本月) | 2000   | 餐飲     | 現金    | 支出 | false       |
        | (本月) | 5000   | 餐飲     | 現金    | 支出 | true        |
      When 使用者查詢預算執行狀況
      Then 操作成功，執行狀況應包含：
        | category | monthly_amount | spent | remaining | is_over_budget |
        | 餐飲     | 8000            | 2000  | 6000      | false           |

  Rule: 後置（回應）- 已結清（advancePaymentStatus=settled）的代墊款交易，計入預算花費統計的有效金額為「總金額 − 代墊金額」；尚未結清的代墊款交易仍以交易總金額計入

    Example: 已結清的代墊款交易只計入總金額扣除代墊金額後的部分
      Given 系統中有以下收支紀錄（本月內）：
        | date         | amount | category | account | type | advancePaymentAmount | advancePaymentStatus |
        | (本月) | 2000   | 餐飲     | 現金    | 支出 |                        |                        |
        | (本月) | 5000   | 餐飲     | 現金    | 支出 | 3000                   | settled                |
      When 使用者查詢預算執行狀況
      Then 操作成功，執行狀況應包含：
        | category | monthly_amount | spent | remaining | is_over_budget |
        | 餐飲     | 8000            | 4000  | 4000      | false           |

    Example: 尚未結清的代墊款交易仍以交易總金額計入預算花費統計
      Given 系統中有以下收支紀錄（本月內）：
        | date         | amount | category | account | type | advancePaymentAmount | advancePaymentStatus |
        | (本月) | 2000   | 餐飲     | 現金    | 支出 |                        |                        |
        | (本月) | 5000   | 餐飲     | 現金    | 支出 | 3000                   | pending                |
      When 使用者查詢預算執行狀況
      Then 操作成功，執行狀況應包含：
        | category | monthly_amount | spent | remaining | is_over_budget |
        | 餐飲     | 8000            | 7000  | 1000      | false           |
