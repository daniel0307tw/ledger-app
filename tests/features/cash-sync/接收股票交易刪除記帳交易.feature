@command
Feature: 接收股票交易刪除記帳交易

  Background:
    Given 系統中有以下帳戶：
      | name   | type   |
      | 永豐銀行 | 一般帳戶 |

  Rule: 前置（參數/狀態）- 必須指定要刪除的記帳交易 id，且該 id 必須對應到一筆 is_stock_sync=true 的既有交易，否則操作失敗
    # 同「接收股票交易更新記帳交易.feature」的合併理由：id 是路徑參數，結構上無法區分「未提供」與「對應不到」。
    Scenario Outline: 依 id 對應情況決定是否可刪除
      Given 系統中有以下記帳交易（stock_analyzer 建立）：
        | id | account | amount | type | isStockSync   |
        | 1  | 永豐銀行 | 100100 | 支出  | <isStockSync> |
      When stock_analyzer 推送刪除現金異動 "<target>"
      Then 操作失敗，錯誤為"找不到該筆收支紀錄"

      Examples:
        | target        | isStockSync |
        | $收支紀錄1.id  | false       |
        | 不存在的id     | true        |

  Rule: 後置（狀態）- 應刪除該筆交易，且不應呼叫既有的 cancel_previous_sync()
    # 依據：這筆交易建立時本來就沒有呼叫過 sync_to_cash_position()（is_transfer=true 且跳過反向同步），
    # 不會有需要清理的 cash_position_id，呼叫 cancel_previous_sync() 是多餘的既有邏輯，不適用於此路徑。
    Example: is_stock_sync=true 交易刪除成功且不觸發同步取消
      Given 系統中有以下記帳交易（stock_analyzer 建立）：
        | id | account | amount | type | isStockSync |
        | 1  | 永豐銀行 | 100100 | 支出  | true        |
      When stock_analyzer 推送刪除現金異動 "$收支紀錄1.id"
      Then 操作成功
      And 收支紀錄 $收支紀錄1.id 應不存在
      And 不應觸發 CashPosition 同步
