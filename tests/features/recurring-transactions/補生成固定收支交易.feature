@command
Feature: 補生成固定收支交易

  Background:
    Given 系統中有以下帳戶：
      | id | name     | type   |
      | 1  | 永豐銀行 | 一般帳戶 |

  Rule: 前置（狀態）- 只對啟用中的規則補生成，已停用的規則不生成

    Example: 規則已停用時不生成
      Given 系統中有以下固定收支規則：
        | id | frequency | amount | category | account  | type | start_date | generate_count | status |
        | 2  | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-06-05 | 5              | 停用   |
      Given 規則 2 已生成以下交易：
        | date       | amount |
        | 2026-06-05 | 15000  |
      When 使用者對規則 2 補生成固定收支交易
      Then 操作成功，本次應補生成 0 筆交易

  Rule: 前置（狀態）- 本輪只提供可被呼叫的 endpoint，由人工觸發（例如透過設定頁的按鈕），不建立自動排程（使用者已確認；未來若要接 Hermes cron 定期觸發，屬於後續獨立的一輪）

  Rule: 後置（狀態）- 只補生成「已生成的未來期數」不足「提前生成期數」設定值的差額，不重複生成已存在的期數

    Example: 已生成 3 期、設定 5 期，補 2 期
      Given 系統中有以下固定收支規則：
        | id | frequency | amount | category | account  | type | start_date | generate_count | status |
        | 1  | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-06-05 | 5              | 啟用   |
      Given 規則 1 已生成以下交易：
        | date       | amount |
        | 2026-06-05 | 15000  |
        | 2026-07-05 | 15000  |
        | 2026-08-05 | 15000  |
      When 使用者對規則 1 補生成固定收支交易
      Then 操作成功，本次應補生成 2 筆交易：
        | date       | amount |
        | 2026-09-05 | 15000  |
        | 2026-10-05 | 15000  |

    Example: 已生成期數已達設定值，補 0 期
      Given 系統中有以下固定收支規則：
        | id | frequency | amount | category | account  | type | start_date | generate_count | status |
        | 1  | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-06-05 | 3              | 啟用   |
      Given 規則 1 已生成以下交易：
        | date       | amount |
        | 2026-06-05 | 15000  |
        | 2026-07-05 | 15000  |
        | 2026-08-05 | 15000  |
      When 使用者對規則 1 補生成固定收支交易
      Then 操作成功，本次應補生成 0 筆交易
