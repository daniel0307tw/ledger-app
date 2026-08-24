@command
Feature: 建立預算

  Background:

  Rule: 前置（參數）- 建立預算必須指定範圍（總預算或分類預算）與每月金額上限；範圍為分類預算時必須指定分類

  Rule: 前置（參數）- 金額必須大於 0

    Example: 金額非正數時建立失敗
      When 使用者建立預算：
        | scope    | category | monthly_amount |
        | 分類預算 | 餐飲     | 0               |
      Then 操作失敗，錯誤為"金額必須為正數"

  Rule: 前置（狀態）- 同一分類不可重複建立分類預算，總預算全系統只能有一筆  # 設計依據：避免同一範圍有多筆金額互相衝突無法判斷以哪筆為準，比照多數記帳 App「一個範圍一個上限」的慣例

    Example: 同一分類重複建立分類預算時失敗
      Given 系統中有以下預算：
        | id | scope    | category | monthly_amount |
        | 1  | 分類預算 | 餐飲     | 8000            |
      When 使用者建立預算：
        | scope    | category | monthly_amount |
        | 分類預算 | 餐飲     | 5000            |
      Then 操作失敗，錯誤為"此分類已設定過預算"

    Example: 總預算重複建立時失敗
      Given 系統中有以下預算：
        | id | scope  | monthly_amount |
        | 1  | 總預算 | 30000           |
      When 使用者建立預算：
        | scope  | monthly_amount |
        | 總預算 | 25000           |
      Then 操作失敗，錯誤為"總預算已存在"

  Rule: 後置（狀態）- 建立成功後，預算立即套用於當月起的執行狀況計算

    Example: 成功建立分類預算
      When 使用者建立預算：
        | scope    | category | monthly_amount |
        | 分類預算 | 餐飲     | 8000            |
      Then 操作成功，預算符合：
        | scope    | category | monthly_amount |
        | 分類預算 | 餐飲     | 8000            |
