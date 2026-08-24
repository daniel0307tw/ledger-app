@query
Feature: 帳戶 — 查詢帳戶列表
  作為 使用者
  我要 查詢我建立的所有帳戶
  以便 在記帳或轉帳時選擇帳戶

  # specs/features/系統抽象.md, specs/features/accounts/句型.md, specs/erm.dbml

  Rule: 後置（回應）- 查詢結果應包含使用者建立的所有帳戶，每個帳戶應包含其類型與目前餘額（餘額 = 該帳戶所有收支紀錄中收入金額加總 - 支出金額加總，含轉帳產生的紀錄）

    Example: 查詢結果應包含所有已建立的帳戶
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
        | 新光銀行 | 一般帳戶 |
      When 使用者查詢帳戶列表
      Then 操作成功，查詢結果應包含：
        | name     | type     | balance |
        | 永豐銀行 | 一般帳戶 | 0       |
        | 新光銀行 | 一般帳戶 | 0       |

    Example: 一般帳戶餘額應正確反映收支紀錄加總，含轉帳產生的紀錄
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
        | 新光銀行 | 一般帳戶 |
      And 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-01-05 | 5000   | 薪資     | 永豐銀行 | 收入 |
        | 2  | 2026-01-06 | 2000   | 餐飲     | 永豐銀行 | 支出 |
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 新光銀行   | 1000   | 2026-01-07 |
      And 使用者查詢帳戶列表
      Then 操作成功，查詢結果應包含：
        | name     | type     | balance |
        | 永豐銀行 | 一般帳戶 | 2000    |
        | 新光銀行 | 一般帳戶 | 1000    |

    Example: 信用卡帳戶因消費計為支出，餘額顯示為負數代表未繳金額
      Given 系統中有以下帳戶：
        | name     | type   |
        | 中國信託 | 信用卡 |
      And 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-01-05 | 3000   | 餐飲     | 中國信託 | 支出 |
      When 使用者查詢帳戶列表
      Then 操作成功，查詢結果應包含：
        | name     | type   | balance |
        | 中國信託 | 信用卡 | -3000   |
