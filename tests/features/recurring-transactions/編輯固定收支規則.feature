@command
Feature: 編輯固定收支規則

  Background:
    Given 系統中有以下帳戶：
      | id | name     | type   |
      | 1  | 永豐銀行 | 一般帳戶 |

  Rule: 前置（狀態）- 規則必須存在，不存在時操作失敗

    Example: 規則不存在時編輯失敗
      When 使用者編輯固定收支規則 999：
        | frequency | amount | category | account  | type | start_date | generate_count |
        | 每月      | 16000  | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              |
      Then 操作失敗，錯誤為"找不到該固定收支規則"

  Rule: 後置（狀態）- 編輯規則（例如改金額/分類）不影響已經生成的未來交易，只影響之後新產生的交易  # 設計依據：比照多數記帳/訂閱類 App 慣例，已生成的具體交易視為獨立事實記錄，修改規則是「往後」生效，不回溯改動既有紀錄

    Example: 編輯金額不影響已生成的交易
      Given 系統中有以下固定收支規則：
        | id | frequency | amount | category | account  | type | start_date | generate_count | status |
        | 1  | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              | 啟用   |
      Given 規則 1 已生成以下交易：
        | date       | amount |
        | 2026-09-05 | 15000  |
        | 2026-10-05 | 15000  |
        | 2026-11-05 | 15000  |
      When 使用者編輯固定收支規則 1：
        | frequency | amount | category | account  | type | start_date | generate_count |
        | 每月      | 16000  | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              |
      Then 操作成功
      And 操作成功，已生成的交易金額應不受影響：
        | date       | amount |
        | 2026-09-05 | 15000  |
        | 2026-10-05 | 15000  |
        | 2026-11-05 | 15000  |
