@command
Feature: 帳戶 — 帳戶間轉帳
  作為 使用者
  我要 在兩個帳戶間轉帳
  以便 反映資金從一個帳戶移到另一個帳戶，且不影響收支報表

  # specs/features/系統抽象.md, specs/features/accounts/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |
      | 新光銀行 |

  Rule: 前置（狀態）- 轉出帳戶與轉入帳戶必須存在

    Scenario Outline: <缺少方> 帳戶不存在時操作失敗
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | <from>       | <to>       | 1000   | 2026-01-05 |
      Then 操作失敗，錯誤為"找不到該帳戶"

      Examples:
        | 缺少方 | from         | to           |
        | 轉出   | 不存在的帳戶 | 新光銀行     |
        | 轉入   | 永豐銀行     | 不存在的帳戶 |

  Rule: 前置（狀態）- 轉出帳戶與轉入帳戶必須不同

    Example: 轉出轉入帳戶相同時操作失敗
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 永豐銀行   | 1000   | 2026-01-05 |
      Then 操作失敗，錯誤為"轉出帳戶與轉入帳戶不可相同"

  Rule: 前置（參數）- 轉帳金額必須為正數

    Example: 金額為 0 時操作失敗
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 新光銀行   | 0      | 2026-01-05 |
      Then 操作失敗，錯誤為"金額必須為正數"

  Rule: 後置（狀態）- 轉帳後應產生一筆轉出紀錄與一筆轉入紀錄，這兩筆皆不計入收支報表

    Example: 轉帳後應建立一筆轉出紀錄與一筆轉入紀錄，並共用同一個轉帳群組
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 新光銀行   | 2000   | 2026-01-05 |
      Then 操作成功
      And 應建立一筆轉出紀錄與一筆轉入紀錄：
        | account  | type | amount | is_transfer | transfer_group_id |
        | 永豐銀行 | 支出 | 2000   | true        | GROUP-1            |
        | 新光銀行 | 收入 | 2000   | true        | GROUP-1            |

  Rule: 後置（狀態）- 轉帳後兩邊帳戶都應同步寫入 stock_analyzer 的 CashPosition，轉出帳戶對應 type=Withdraw、轉入帳戶對應 type=Deposit，currency 固定為 TWD
    # 實作 Phase 05 時發現的規格缺口，已與使用者確認：轉帳是兩個帳戶間的現金移動，若不同步，stock_analyzer 各帳戶的現金部位會與實際不符。同步失敗處理方式比照「新增收支紀錄」：不擋下轉帳本身，標記待重試。

    Example: 轉帳後兩筆紀錄應分別同步至 CashPosition 的正確方向
      When 使用者將帳戶轉帳：
        | from_account | to_account | amount | date       |
        | 永豐銀行     | 新光銀行   | 2000   | 2026-01-05 |
      Then 操作成功
      And stock_analyzer 的 CashPosition 應新增兩筆：
        | institution | type     | amount | currency |
        | 永豐銀行    | Withdraw | 2000   | TWD      |
        | 新光銀行    | Deposit  | 2000   | TWD      |
