@command
Feature: 收支紀錄 — 新增收支紀錄
  作為 使用者
  我要 新增一筆收支紀錄
  以便 記錄日常收支，並同步更新股票分析系統的現金部位

  # specs/features/系統抽象.md, specs/features/transactions/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 前置（參數）- 日期、金額、分類、帳戶、類型必須提供，備註可省略

    Scenario Outline: 缺少 <缺少參數> 時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type   |
        | <date>     | <amount> | <category> | <account> | <type> |
      Then 操作失敗，錯誤為"必要參數未提供"

      Examples:
        | 缺少參數 | date       | amount | category | account  | type |
        | 日期     |            | 100    | 餐飲     | 永豐銀行 | 支出 |
        | 金額     | 2026-01-05 |        | 餐飲     | 永豐銀行 | 支出 |
        | 分類     | 2026-01-05 | 100    |          | 永豐銀行 | 支出 |
        | 帳戶     | 2026-01-05 | 100    | 餐飲     |          | 支出 |
        | 類型     | 2026-01-05 | 100    | 餐飲     | 永豐銀行 |      |

  Rule: 前置（參數）- 金額必須為正數

    Example: 金額為 0 時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 0      | 餐飲     | 永豐銀行 | 支出 |
      Then 操作失敗，錯誤為"金額必須為正數"

  Rule: 前置（狀態）- 交易所屬帳戶必須存在

    Example: 帳戶不存在時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category | account      | type |
        | 2026-01-05 | 100    | 餐飲     | 不存在的帳戶 | 支出 |
      Then 操作失敗，錯誤為"找不到該帳戶"

  Rule: 前置（狀態）- 交易所屬分類必須存在

    Example: 分類不存在時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category     | account  | type |
        | 2026-01-05 | 100    | 不存在的分類 | 永豐銀行 | 支出 |
      Then 操作失敗，錯誤為"找不到該分類"

  Rule: 前置（狀態）- 交易所屬分類的收支類型必須與交易本身的類型相符（分類類型為「皆可」時兩種交易類型皆可用），此規則於後端 service 層強制驗證，比照既有 CATEGORY_NOT_FOUND、ACCOUNT_NOT_FOUND 驗證規則的慣例

    Example: 分類收支類型與交易類型不符時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 100    | 薪資     | 永豐銀行 | 支出 |
      Then 操作失敗，錯誤為"分類收支類型與交易類型不符"

    Example: 分類收支類型為皆可時支出交易可成功使用該分類
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 100    | 校正回歸 | 永豐銀行 | 支出 |
      Then 操作成功

  Rule: 後置（狀態）- 新增後應建立一筆收支紀錄

    Example: 新增後應建立一筆內容相符的收支紀錄
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type | note |
        | 2026-01-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 聚餐 |
      Then 操作成功，結果符合：
        | date       | amount | category | account  | type | note |
        | 2026-01-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 聚餐 |

  Rule: 後置（狀態）- 新增後應同步寫入 stock_analyzer 的 CashPosition，institution 為交易所屬帳戶名稱，類型為支出對應 type=Withdraw、類型為收入對應 type=Deposit，currency 固定為 TWD

    Scenario Outline: 新增<type>後同步至 CashPosition 的 <cash_type>
      When 使用者建立收支紀錄：
        | date       | amount   | category   | account  | type   |
        | 2026-01-05 | <amount> | <category> | 永豐銀行 | <type> |
      Then 操作成功
      And 收支紀錄的同步狀態應為 "synced"
      And stock_analyzer 的 CashPosition 應新增一筆：
        | institution | type        | amount   | currency |
        | 永豐銀行    | <cash_type> | <amount> | TWD      |

      Examples:
        | type | cash_type | amount | category |
        | 支出 | Withdraw  | 4000   | 餐飲     |
        | 收入 | Deposit   | 5000   | 薪資     |

  Rule: 前置（狀態）- 代墊金額（advancePaymentAmount）僅限支出交易可用，收入交易設定則操作失敗

    Example: 設定代墊金額用於收入交易時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 收入 | 3000                   |
      Then 操作失敗，錯誤為"代墊款標記僅限支出交易"

  Rule: 前置（參數）- 代墊金額不可超過交易總金額

    Example: 代墊金額超過總金額時操作失敗
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 5000                   |
      Then 操作失敗，錯誤為"代墊金額不可超過交易總金額"

  Rule: 後置（狀態）- 標記代墊金額的支出交易，在收到還款前，交易總金額仍照現行邏輯正常計入支出/預算/報表（代墊金額只是總金額中的一部分，不是另外開一筆）

    Example: 新增含代墊金額的交易後應正常建立，結清狀態為未結清
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   |
      Then 操作成功，結果符合：
        | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | pending               |

    Example: 代墊金額等於總金額時（整筆皆為代墊款）應正常建立
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-05 | 1000   | 餐飲     | 永豐銀行 | 支出 | 1000                   |
      Then 操作成功，結果符合：
        | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 2026-08-05 | 1000   | 餐飲     | 永豐銀行 | 支出 | 1000                   | pending               |

  Rule: 後置（狀態）- 若同步 CashPosition 失敗，收支紀錄仍應建立成功，並標記為待重試

    Example: 外部同步失敗時交易仍建立成功並標記待重試
      Given stock_analyzer 的資料庫暫時無法寫入
      When 使用者建立收支紀錄：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 1000   | 餐飲     | 永豐銀行 | 支出 |
      Then 操作成功
      And 收支紀錄的同步狀態應為 "pending"
