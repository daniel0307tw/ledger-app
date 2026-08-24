@query
Feature: 查詢固定收支規則列表

  Background:
    Given 系統中有以下帳戶：
      | id | name     | type   |
      | 1  | 永豐銀行 | 一般帳戶 |

  Rule: 後置（回應）- 查詢結果應包含所有固定收支規則（啟用中與已停用皆列出），含頻率/金額/分類/帳戶/下次生成日期等資訊

    Example: 查詢結果包含啟用與停用的規則
      Given 系統中有以下固定收支規則：
        | id | frequency | amount | category | account  | type | start_date | generate_count | status |
        | 1  | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              | 啟用   |
        | 2  | 每年      | 3000   | 居家     | 永豐銀行 | 支出 | 2026-01-01 | 1              | 停用   |
      When 使用者查詢固定收支規則列表
      Then 操作成功，查詢結果應包含以下固定收支規則：
        | id | frequency | amount | status |
        | 1  | 每月      | 15000  | 啟用   |
        | 2  | 每年      | 3000   | 停用   |
