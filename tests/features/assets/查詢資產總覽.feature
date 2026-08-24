@query
Feature: 資產 — 查詢資產總覽
  作為 使用者
  我要 查詢彙整現金、信用卡負債與股票市值的資產總覽
  以便 一次掌握所有資產與負債的現況

  # specs/features/系統抽象.md, specs/features/assets/句型.md, specs/erm.dbml

  Rule: 後置（回應）- 現金總額應為一般帳戶 balance 加總

    Example: 現金總額應正確反映一般帳戶收支加總
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 50000  | 薪資     | 永豐銀行 | 收入 |
        | 2  | 2026-08-10 | 20000  | 餐飲     | 永豐銀行 | 支出 |
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下現金與信用卡總額：
        | cash_total | credit_card_debt_total |
        | 30000      | 0                       |

  Rule: 後置（回應）- 信用卡負債總額應為信用卡帳戶 balance 加總（本為負數）

    Example: 信用卡負債總額應正確反映信用卡帳戶消費加總
      Given 系統中有以下帳戶：
        | name     | type   |
        | 台新信用卡 | 信用卡 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account    | type |
        | 1  | 2026-08-05 | 8000   | 餐飲     | 台新信用卡 | 支出 |
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下現金與信用卡總額：
        | cash_total | credit_card_debt_total |
        | 0          | -8000                  |

  Rule: 後置（回應）- 股票市值應依市場分 TWD（台股）/USD（美股），來自 stock_analyzer 唯讀 API

    Example: 股票市值應依市場分幣別呈現
      Given stock_analyzer 有以下股票持倉：
        | currency | symbol | name     | market_value | unrealized_pnl |
        | TWD      | 2330   | 台積電   | 150000        | 20000           |
        | USD      | AAPL   | 蘋果     | 5000          | 500             |
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下幣別資產小計：
        | currency | total  |
        | TWD      | 150000 |
        | USD      | 5000   |

  Rule: 後置（回應）- 查詢結果應包含股票個股明細（symbol、name、市值、損益）

    Example: 查詢結果應包含每檔股票的個股明細
      Given stock_analyzer 有以下股票持倉：
        | currency | symbol | name     | market_value | unrealized_pnl |
        | TWD      | 2330   | 台積電   | 150000        | 20000           |
        | USD      | AAPL   | 蘋果     | 5000          | 500             |
      When 使用者查詢資產總覽
      Then 查詢結果應包含以下股票個股明細：
        | currency | symbol | name   | market_value | unrealized_pnl |
        | TWD      | 2330   | 台積電 | 150000        | 20000           |
        | USD      | AAPL   | 蘋果   | 5000          | 500             |

  Rule: 後置（回應）- 資產總額應依幣別（TWD/USD）分別小計，不做匯率換算、不合併成單一數字

    Example: TWD 與 USD 資產應各自獨立小計，不互相換算合併
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 30000  | 薪資     | 永豐銀行 | 收入 |
      Given stock_analyzer 有以下股票持倉：
        | currency | symbol | name   | market_value | unrealized_pnl |
        | TWD      | 2330   | 台積電 | 150000        | 20000           |
        | USD      | AAPL   | 蘋果   | 5000          | 500             |
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下幣別資產小計：
        | currency | total  |
        | TWD      | 180000 |
        | USD      | 5000   |

  Rule: 後置（回應）- 股票資料來源（stock_analyzer API）查詢失敗時，現金與信用卡總額仍應正常回傳，股票部分應標示查詢失敗（partial failure，非整頁失敗）

    Example: 股票資料查詢失敗時現金與信用卡仍正常顯示
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 10000  | 薪資     | 永豐銀行 | 收入 |
      Given stock_analyzer 的股票資料查詢服務暫時無法連線
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下現金與信用卡總額：
        | cash_total | credit_card_debt_total |
        | 10000      | 0                       |
      And 查詢結果中的股票資料應標示查詢失敗

  Rule: 後置（回應）- 股票市值為 0（尚無持股）時應顯示 0 並標示尚無持股

    Example: 尚無持股時股票市值顯示為 0 並標示提示
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 10000  | 薪資     | 永豐銀行 | 收入 |
      Given stock_analyzer 尚無任何股票持倉
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下幣別資產小計：
        | currency | total |
        | TWD      | 10000 |
      And 查詢結果應包含以下股票個股明細：
        | currency | symbol | name | market_value | unrealized_pnl |
      And 查詢結果應顯示尚無持股

  Rule: 後置（回應）- 尚未建立任何帳戶時，現金與信用卡負債總額應顯示為 0

    Example: 尚未建立任何帳戶時現金與信用卡負債總額為 0
      When 使用者查詢資產總覽
      Then 操作成功，查詢結果應包含以下現金與信用卡總額：
        | cash_total | credit_card_debt_total |
        | 0          | 0                       |
