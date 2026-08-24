@command
Feature: 編輯預算

  Rule: 前置（狀態）- 預算必須存在，不存在時操作失敗

    Example: 預算不存在時編輯失敗
      When 使用者編輯預算 999：
        | monthly_amount |
        | 10000           |
      Then 操作失敗，錯誤為"找不到該預算"

  Rule: 後置（狀態）- 編輯金額後，當月執行狀況查詢應立即反映新的上限（不是下個月才生效）  # 設計依據：預算上限是設定值不是歷史記錄，比照一般設定類欄位即時生效的慣例

    Example: 編輯金額成功
      Given 系統中有以下預算：
        | id | scope    | category | monthly_amount |
        | 1  | 分類預算 | 餐飲     | 8000            |
      When 使用者編輯預算 1：
        | monthly_amount |
        | 10000           |
      Then 操作成功
