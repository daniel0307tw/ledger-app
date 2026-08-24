@command
Feature: 資產 — 刷新資產總覽
  作為 使用者
  我要 主動刷新資產總覽，觸發股票現值更新
  以便 在需要的時候（例如下拉刷新）看到最新的股票市價，而不是等被動查詢時顯示舊快照

  # specs/features/系統抽象.md, specs/features/assets/句型.md, specs/erm.dbml
  #
  # 與「查詢資產總覽」的差異：查詢是唯讀，回傳 stock_analyzer 上次落地保存的股票市價
  # 快照；刷新會呼叫 stock_analyzer 的刷新端點，真的去外部股價 API 抓最新市價、落地
  # 保存新快照後才回傳——會消耗外部股價 API 額度，只給使用者主動觸發時呼叫，不應被
  # 頻繁輪詢或每次進頁面就自動呼叫。

  Rule: 後置（狀態）- 操作應呼叫 stock_analyzer 的刷新端點（POST），而非唯讀查詢端點，觸發即時股價更新並落地保存新快照

    Example: 刷新資產總覽應呼叫股票資料來源的刷新端點
      Given stock_analyzer 有以下股票持倉：
        | currency | symbol | name   | market_value | unrealized_pnl |
        | TWD      | 2330   | 台積電 | 150000        | 20000           |
      When 使用者刷新資產總覽
      Then 操作應呼叫股票資料來源的刷新端點

  Rule: 後置（回應）- 回應內容格式與「查詢資產總覽」相同（現金/信用卡總額、股票個股明細、幣別資產小計）

    Example: 刷新後應回傳與查詢資產總覽相同格式的完整結果
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 30000  | 薪資     | 永豐銀行 | 收入 |
      Given stock_analyzer 有以下股票持倉：
        | currency | symbol | name   | market_value | unrealized_pnl |
        | TWD      | 2330   | 台積電 | 150000        | 20000           |
      When 使用者刷新資產總覽
      Then 操作成功，查詢結果應包含以下現金與信用卡總額：
        | cash_total | credit_card_debt_total |
        | 30000      | 0                       |
      And 查詢結果應包含以下幣別資產小計：
        | currency | total  |
        | TWD      | 180000 |

  Rule: 後置（回應）- 刷新時股票資料來源查詢失敗，現金與信用卡總額仍應正常回傳，股票部分應標示查詢失敗，比照「查詢資產總覽」既有的 partial failure 慣例

    Example: 刷新失敗時現金與信用卡仍正常顯示
      Given 系統中有以下帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account  | type |
        | 1  | 2026-08-05 | 10000  | 薪資     | 永豐銀行 | 收入 |
      Given stock_analyzer 的股票資料查詢服務暫時無法連線
      When 使用者刷新資產總覽
      Then 操作成功，查詢結果應包含以下現金與信用卡總額：
        | cash_total | credit_card_debt_total |
        | 10000      | 0                       |
      And 查詢結果中的股票資料應標示查詢失敗
