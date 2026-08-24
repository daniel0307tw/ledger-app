@command
Feature: 收支紀錄 — 刪除收支紀錄
  作為 使用者
  我要 刪除一筆既有的收支紀錄
  以便 移除記錯的紀錄，並讓股票分析系統的現金部位反映最新內容

  # specs/features/系統抽象.md, specs/features/transactions/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 前置（狀態）- 欲刪除的收支紀錄必須存在

    Example: 紀錄不存在時操作失敗
      When 使用者刪除收支紀錄 "不存在的id"
      Then 操作失敗，錯誤為"找不到該筆收支紀錄"

  Rule: 後置（狀態）- 刪除後該筆收支紀錄應不再存在

    Example: 刪除後該筆紀錄應不再存在
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | sync_status |
        | 1  | 2026-01-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | synced      |
      When 使用者刪除收支紀錄 $收支紀錄1.id
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 應不存在

  Rule: 後置（狀態）- 刪除一筆「還款交易」（即某筆代墊款交易的 settlement_transaction_id 所指向的那筆收入交易）時，原代墊款交易的結清狀態應復原為未結清，並解除彼此的關聯

    Example: 刪除還款交易後原代墊款交易復原為未結清
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus | settlementTransactionId |
        | 2  | 2026-08-06 | 3000   | 餐飲     | 永豐銀行 | 收入 |                        |                        |                          |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled               | $收支紀錄2.id            |
      When 使用者刪除收支紀錄 $收支紀錄2.id
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 的代墊款狀態應為 "pending"

  Rule: 後置（狀態）- 若該筆先前已同步至 CashPosition，刪除後應同步刪除對應的 CashPosition 那筆；若該筆先前的同步仍處於待重試狀態，應取消原本的待重試任務，不再嘗試同步

    Example: 刪除已同步的紀錄後對應的 CashPosition 也應被移除
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | sync_status |
        | 1  | 2026-01-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | synced      |
      When 使用者刪除收支紀錄 $收支紀錄1.id
      Then 操作成功
      And stock_analyzer 的 CashPosition 不應再包含收支紀錄 $收支紀錄1.id 對應的那筆
