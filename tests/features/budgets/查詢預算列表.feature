@query
Feature: 查詢預算列表

  Rule: 後置（回應）- 查詢結果應包含所有已設定的預算（總預算+各分類預算），含範圍/分類名稱/金額上限

    Example: 查詢結果包含總預算與分類預算
      Given 系統中有以下預算：
        | id | scope    | category | monthly_amount |
        | 1  | 總預算   |          | 30000           |
        | 2  | 分類預算 | 餐飲     | 8000            |
      When 使用者查詢預算列表
      Then 操作成功，查詢結果應包含以下預算：
        | scope    | category | monthly_amount |
        | 總預算   |          | 30000           |
        | 分類預算 | 餐飲     | 8000            |
