@command
Feature: 刪除固定收支規則

  Background:
    Given 系統中有以下帳戶：
      | id | name     | type   |
      | 1  | 永豐銀行 | 一般帳戶 |

  Rule: 前置（狀態）- 規則必須存在，不存在時操作失敗

    Example: 規則不存在時刪除失敗
      When 使用者刪除固定收支規則 999
      Then 操作失敗，錯誤為"找不到該固定收支規則"

  Rule: 後置（狀態）- 刪除規則後，已經生成的未來 ledger_transaction 應保留不刪除，只是不再產生新的交易  # 設計依據：已生成的交易是真實記帳資料（使用者可能已經看過/核對過），刪除規則視為「停止訂閱」而非「撤銷歷史」，比照多數訂閱管理慣例

    Example: 刪除規則後已生成的交易保留
      Given 系統中有以下固定收支規則：
        | id | frequency | amount | category | account  | type | start_date | generate_count | status |
        | 1  | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              | 啟用   |
      Given 規則 1 已生成以下交易：
        | date       | amount |
        | 2026-09-05 | 15000  |
        | 2026-10-05 | 15000  |
      When 使用者刪除固定收支規則 1
      Then 操作成功，規則已刪除但以下交易應仍存在：
        | date       | amount |
        | 2026-09-05 | 15000  |
        | 2026-10-05 | 15000  |
