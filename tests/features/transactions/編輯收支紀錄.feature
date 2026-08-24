@command
Feature: 收支紀錄 — 編輯收支紀錄
  作為 使用者
  我要 編輯一筆既有的收支紀錄
  以便 修正輸入錯誤，並讓股票分析系統的現金部位反映最新內容

  # specs/features/系統抽象.md, specs/features/transactions/句型.md, specs/erm.dbml

  Background:
    Given 系統中有以下帳戶：
      | name     |
      | 永豐銀行 |

  Rule: 前置（狀態）- 欲編輯的收支紀錄必須存在

    Example: 紀錄不存在時操作失敗
      When 使用者編輯收支紀錄 "不存在的id"：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 100    | 餐飲     | 永豐銀行 | 支出 |
      Then 操作失敗，錯誤為"找不到該筆收支紀錄"

  Rule: 前置（參數）- 編輯後的日期、金額、分類、帳戶、類型必須符合與「新增收支紀錄」相同的驗證規則（含分類必須存在、分類收支類型須與交易類型相符）

    Example: 編輯後金額為 0 時操作失敗
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | sync_status |
        | 1  | 2026-01-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | synced      |
      When 使用者編輯收支紀錄 $收支紀錄1.id：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 0      | 餐飲     | 永豐銀行 | 支出 |
      Then 操作失敗，錯誤為"金額必須為正數"

  Rule: 後置（狀態）- 編輯後應更新該筆收支紀錄的內容

    Example: 編輯後應更新紀錄內容
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | sync_status |
        | 1  | 2026-01-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | synced      |
      When 使用者編輯收支紀錄 $收支紀錄1.id：
        | date       | amount | category | account  | type |
        | 2026-01-06 | 4500   | 交通     | 永豐銀行 | 支出 |
      Then 操作成功，結果符合：
        | date       | amount | category | account  | type |
        | 2026-01-06 | 4500   | 交通     | 永豐銀行 | 支出 |

  Rule: 後置（狀態）- 編輯一筆已結清（advance_payment_status=settled）的代墊款交易的總金額或代墊金額時，允許編輯，但應自動將該筆的結清狀態改回未結清，並解除與原還款交易的關聯；已建立的還款收入交易本身不連動變更（因為結清時計算的「有效支出金額」是根據編輯前的總金額與代墊金額算出的，兩者任一改變都會讓舊的結清結果失真）

    Example: 編輯已結清代墊款交易的總金額後自動取消結清
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled               |
      When 使用者編輯收支紀錄 $收支紀錄1.id：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-05 | 4500   | 餐飲     | 永豐銀行 | 支出 | 3000                   |
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 的代墊款狀態應為 "pending"

    # 注意：本 PUT endpoint 採全量覆寫（比照 date/category/account/type 等其他欄位的既有慣例），
    # 若編輯時完全不帶 advancePaymentAmount 欄位，等同於使用者主動清空代墊金額，而非「保留原值、
    # 只改總金額」——上面這個 Example 因此在 When 明確重帶原本的 3000，測試的是「只改總金額」
    # 這個情境本身；「編輯時清空代墊金額」是另一個未被本檔涵蓋的獨立情境，交由前端表單保證
    # 編輯代墊款交易時一律重新帶入既有的 advancePaymentAmount。

    Example: 編輯已結清代墊款交易的代墊金額後自動取消結清
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | advancePaymentAmount | advancePaymentStatus |
        | 1  | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 3000                   | settled               |
      When 使用者編輯收支紀錄 $收支紀錄1.id：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-05 | 4000   | 餐飲     | 永豐銀行 | 支出 | 2500                   |
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 的代墊款狀態應為 "pending"

  Rule: 後置（狀態）- 編輯一筆原本沒有代墊款的交易，第一次加上代墊金額時，應將該筆的代墊款狀態設為未結清（pending），使其會出現在待收回代墊款清單中

    Example: 編輯時第一次加上代墊金額應設為未結清
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-20 | 4580   | 娛樂     | 永豐銀行 | 支出 |
      When 使用者編輯收支紀錄 $收支紀錄1.id：
        | date       | amount | category | account  | type | advancePaymentAmount |
        | 2026-08-20 | 4580   | 娛樂     | 永豐銀行 | 支出 | 3110                   |
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 的代墊款狀態應為 "pending"

  Rule: 後置（狀態）- 若該筆先前已同步至 CashPosition，編輯後應同步更新對應的 CashPosition 那筆；若該筆先前的同步仍處於待重試狀態，應取消原本的待重試任務，改依編輯後的新內容重新嘗試一次同步

    Example: 編輯先前待重試的紀錄後應重新嘗試同步
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type | sync_status |
        | 1  | 2026-01-05 | 1000   | 餐飲     | 永豐銀行 | 支出 | pending     |
      When 使用者編輯收支紀錄 $收支紀錄1.id：
        | date       | amount | category | account  | type |
        | 2026-01-05 | 1500   | 餐飲     | 永豐銀行 | 支出 |
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 的同步狀態應為 "synced"
      And stock_analyzer 的 CashPosition 應新增一筆：
        | institution | type     | amount | currency |
        | 永豐銀行    | Withdraw | 1500   | TWD      |
