@command
Feature: 接收股票交易建立記帳交易

  Background:
    Given 系統中有以下帳戶：
      | name   | type   |
      | 永豐銀行 | 一般帳戶 |
      | 新光銀行 | 一般帳戶 |

  Rule: 前置（參數）- 必須提供方向（支出/收入）、金額、幣別、對應帳戶名稱
    Example: 缺少對應帳戶名稱時操作失敗
      When stock_analyzer 推送以下現金異動：
        | direction | amount | currency |
        | 支出       | 100100 | TWD      |
      Then 操作失敗，錯誤為"必要參數未提供"

  Rule: 前置（狀態）- 對應帳戶名稱必須存在於既有 account 表
    Example: 帳戶不存在時操作失敗
      When stock_analyzer 推送以下現金異動：
        | direction | amount | currency | accountName |
        | 支出       | 100100 | TWD      | 凱基銀行     |
      Then 操作失敗，錯誤為"找不到該帳戶"

  Rule: 後置（狀態）- 建立的 ledger_transaction 應標記 is_stock_sync=true、category_id=null、is_transfer=true，記錄推送當下的實際幣別，且不應呼叫既有的 sync_to_cash_position()
    # 涵蓋以下已確認的原子 Rule：
    # - 標記 is_stock_sync=true；category_id=null、is_transfer=true（比照既有轉帳模式，不計入報表/預算）
    # - 記錄推送當下的實際幣別 TWD 或 USD
    # - 不呼叫既有的 sync_to_cash_position()，不寫入 stock_analyzer 的 cash_position（避免雙重計算）
    # - 操作成功時回傳這筆記帳交易的 id（由「新建立的記帳交易應符合」步驟一併驗證 id 存在）
    Scenario Outline: 依方向與幣別建立記帳交易，不觸發 CashPosition 同步
      When stock_analyzer 推送以下現金異動：
        | direction   | amount   | currency   | accountName |
        | <direction> | <amount> | <currency> | <account>   |
      Then 操作成功
      And 新建立的記帳交易應符合：
        | type        | amount   | currency   | isStockSync | isTransfer | categoryId |
        | <direction> | <amount> | <currency> | true        | true       |            |
      And 不應觸發 CashPosition 同步

      Examples:
        | direction | amount | currency | account |
        | 支出       | 100100 | TWD      | 永豐銀行 |
        | 收入       | 495    | USD      | 新光銀行 |
