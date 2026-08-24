@command
Feature: 建立固定收支規則

  Background:
    Given 系統中有以下帳戶：
      | id | name     | type   |
      | 1  | 永豐銀行 | 一般帳戶 |

  Rule: 前置（參數）- 建立規則必須提供頻率（每天/每週/每月/每季/每年/每三年）、金額、分類、帳戶、類型、起始日期、提前生成期數

  Rule: 前置（參數）- 金額必須大於 0，比照既有收支紀錄的驗證規則

    Example: 金額非正數時建立失敗
      When 使用者建立固定收支規則：
        | frequency | amount | category | account  | type | start_date | generate_count |
        | 每月      | 0      | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              |
      Then 操作失敗，錯誤為"金額必須為正數"

  Rule: 後置（狀態）- 建立規則後，應依頻率與起始日期，立即建立「提前生成期數」指定的未來筆數的 ledger_transaction（真實交易，非僅規則本身）

    Example: 每月頻率建立 3 期，生成 3 筆遞增交易
      When 使用者建立固定收支規則：
        | frequency | amount | category | account  | type | start_date | generate_count |
        | 每月      | 15000  | 居家     | 永豐銀行 | 支出 | 2026-09-05 | 3              |
      Then 操作成功，規則符合：
        | frequency | amount | category | account  | generate_count |
        | 每月      | 15000  | 居家     | 永豐銀行 | 3              |
      And 操作成功，應生成以下 3 筆交易：
        | date       | amount | category | account  | type |
        | 2026-09-05 | 15000  | 居家     | 永豐銀行 | 支出 |
        | 2026-10-05 | 15000  | 居家     | 永豐銀行 | 支出 |
        | 2026-11-05 | 15000  | 居家     | 永豐銀行 | 支出 |

  Rule: 後置（狀態）- 未來日期的交易照常計入既有行事曆/報表頁面的當月/當期統計，不特別排除或另外顯示（使用者已確認）

  Rule: 後置（狀態）- 規則建立成功後應標記為啟用狀態
