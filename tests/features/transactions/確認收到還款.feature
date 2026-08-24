@command
Feature: 收支紀錄 — 確認收到還款
  作為 使用者
  我要 對一筆含代墊款的交易確認收到還款
  以便 記錄款項已收回，讓這筆代墊款不再計入我的支出統計

  # specs/features/系統抽象.md, specs/features/transactions/句型.md, specs/erm.dbml
  # 一筆交易的總金額（amount）可能只有部分是代墊款（advancePaymentAmount，例如聚餐總額 4000，
  # 其中 3000 是幫朋友代墊、1000 是自己吃的），確認收到還款只針對代墊金額那一部分，
  # 不是整筆交易金額。

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 前置（狀態）- 欲確認收到還款的收支紀錄必須存在

    Example: 紀錄不存在時操作失敗
      When 使用者對收支紀錄 "不存在的id" 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 3000   | 永豐銀行 |
      Then 操作失敗，錯誤為"找不到該筆收支紀錄"

  Rule: 前置（狀態）- 欲確認收到還款的收支紀錄必須含代墊金額（advancePaymentAmount 不為 null）的支出交易

    Example: 對不含代墊金額的交易確認收到還款時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 3000   | 永豐銀行 |
      Then 操作失敗，錯誤為"該筆交易非代墊款交易"

  Rule: 前置（狀態）- 該筆代墊款交易必須尚未結清（advance_payment_status=pending）

    Example: 對已結清的代墊款交易重複確認時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 3000   | 永豐銀行 |
      Then 操作失敗，錯誤為"該筆代墊款已結清"

  Rule: 前置（參數）- 還款日期、還款金額、入帳帳戶必須提供

    Scenario Outline: 缺少 <缺少參數> 時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date   | amount   | account   |
        | <date> | <amount> | <account> |
      Then 操作失敗，錯誤為"必要參數未提供"

      Examples:
        | 缺少參數 | date       | amount | account  |
        | 日期     |            | 3000   | 永豐銀行 |
        | 金額     | 2026-08-06 |        | 永豐銀行 |
        | 帳戶     | 2026-08-06 | 3000   |          |

  Rule: 前置（參數）- 還款金額必須等於原交易的代墊金額（advancePaymentAmount，不是交易總金額），只支援全額還款，金額不符則操作失敗

    Example: 還款金額等於交易總金額但不等於代墊金額時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 4000   | 永豐銀行 |
      Then 操作失敗，錯誤為"還款金額與代墊金額不符，僅支援全額還款"

    Example: 還款金額與代墊金額不符時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 2500   | 永豐銀行 |
      Then 操作失敗，錯誤為"還款金額與代墊金額不符，僅支援全額還款"

  Rule: 前置（狀態）- 入帳帳戶必須存在

    Example: 入帳帳戶不存在時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account      |
        | 2026-08-06 | 3000   | 不存在的帳戶 |
      Then 操作失敗，錯誤為"找不到該帳戶"

  Rule: 後置（狀態）- 確認成功後應建立一筆收入交易，金額等於代墊金額、日期同還款內容、帳戶為指定的入帳帳戶

    Example: 全額還款成功後應建立對應的還款收入交易，金額等於代墊金額而非交易總金額
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 3000   | 永豐銀行 |
      Then 操作成功
      And 應建立一筆收支紀錄：
        | date       | amount | account  | type |
        | 2026-08-06 | 3000   | 永豐銀行 | 收入 |

  Rule: 後置（狀態）- 確認成功後應將原代墊款交易標記為已結清（advance_payment_status=settled），並關聯至新建立的還款收入交易（settlement_transaction_id）；交易本身的 amount（總金額）不變，只有結清狀態改變

    Example: 全額還款成功後原代墊款交易應標記為已結清
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 3000   | 永豐銀行 |
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 的代墊款狀態應為 "settled"

  Rule: 後置（狀態）- 新建立的還款收入交易應同步寫入 stock_analyzer 的 CashPosition，比照既有「新增收支紀錄」的同步慣例（type=Deposit）

    Example: 確認收到還款後新建立的還款交易應同步至 CashPosition
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending                |
      When 使用者對收支紀錄 $收支紀錄1.id 確認收到還款：
        | date       | amount | account  |
        | 2026-08-06 | 3000   | 永豐銀行 |
      Then 操作成功
      And stock_analyzer 的 CashPosition 應新增一筆：
        | institution | type    | amount | currency |
        | 永豐銀行    | Deposit | 3000   | TWD      |
