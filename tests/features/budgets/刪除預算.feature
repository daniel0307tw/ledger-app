@command
Feature: 刪除預算

  Rule: 前置（狀態）- 預算必須存在，不存在時操作失敗

    Example: 預算不存在時刪除失敗
      When 使用者刪除預算 999
      Then 操作失敗，錯誤為"找不到該預算"

  Rule: 後置（狀態）- 刪除後該範圍不再有上限，執行狀況查詢不再列出該筆

    Example: 刪除成功
      Given 系統中有以下預算：
        | id | scope    | category | monthly_amount |
        | 1  | 分類預算 | 餐飲     | 8000            |
      When 使用者刪除預算 1
      Then 操作成功
