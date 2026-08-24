@query
Feature: 收支紀錄 — 查詢待收回代墊款清單
  作為 使用者
  我要 查詢目前尚未收回的代墊款交易清單
  以便 知道有哪些墊款還在等對方歸還

  # specs/features/系統抽象.md, specs/features/transactions/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 後置（回應）- 查詢結果應為所有 advancePaymentAmount 不為 null 且 advancePaymentStatus=pending 的支出交易，含交易總金額與代墊金額

    Example: 查詢結果應包含所有未結清的代墊款交易
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
        | 2  | 2026-08-06 | 300    | 交通     | 永豐銀行 | 支出 |                        |                        |
      When 使用者查詢待收回代墊款清單
      Then 操作成功，查詢結果應包含以下待收回代墊款：
        | date       | amount | category | account  | advancePaymentAmount |
        | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 3000                   |

  Rule: 後置（回應）- 已結清（advancePaymentStatus=settled）的代墊款交易不應出現在清單中

    Example: 已結清的代墊款交易不出現在清單中
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled                |
      When 使用者查詢待收回代墊款清單
      Then 操作成功，查詢結果應包含以下待收回代墊款：
        | date | amount | category | account | advancePaymentAmount |

  Rule: 後置（回應）- 目前沒有任何待收回的代墊款交易時，查詢結果為空

    Example: 沒有任何代墊款交易時查詢結果為空
      When 使用者查詢待收回代墊款清單
      Then 操作成功，查詢結果應包含以下待收回代墊款：
        | date | amount | category | account | advancePaymentAmount |
