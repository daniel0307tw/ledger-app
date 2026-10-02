@command
Feature: 接收股票交易更新記帳交易

  Background:
    Given 系統中有以下帳戶：
      | name   | type   |
      | 永豐銀行 | 一般帳戶 |

  Rule: 前置（參數/狀態）- 必須指定要更新的記帳交易 id，且該 id 必須對應到一筆 is_stock_sync=true 的既有交易，否則操作失敗
    # 「必須指定 id」原為獨立 Rule，但 id 是既有 API 設計（Phase 04）中的路徑參數，
    # 結構上不存在「有提供但為空」與「對應不到既有交易」的差異，故與此 Rule 合併，
    # 不重複建立無法區分的 Scenario（Phase 05 實作時的簡化，原子 Rule 意圖保留於此標題）。
    Scenario Outline: 依 id 對應情況決定是否可更新
      Given 系統中有以下記帳交易（stock_analyzer 建立）：
        | id | account | amount | type | isStockSync   |
        | 1  | 永豐銀行 | 100100 | 支出  | <isStockSync> |
      When stock_analyzer 推送更新現金異動 "<target>"：
        | amount | direction |
        | 200000 | 收入      |
      Then 操作失敗，錯誤為"找不到該筆收支紀錄"

      Examples:
        | target        | isStockSync |
        | $收支紀錄1.id  | false       |
        | 不存在的id     | true        |

  Rule: 後置（狀態）- 應更新該筆交易的金額與方向（type），且不應呼叫既有的 sync_to_cash_position() / cancel_previous_sync()
    Example: is_stock_sync=true 交易更新成功且不觸發同步
      Given 系統中有以下記帳交易（stock_analyzer 建立）：
        | id | account | amount | type | isStockSync |
        | 1  | 永豐銀行 | 100100 | 支出  | true        |
      When stock_analyzer 推送更新現金異動 "$收支紀錄1.id"：
        | amount | direction |
        | 200000 | 收入      |
      Then 操作成功
      And 記帳交易 "$收支紀錄1.id" 應符合：
        | amount | type |
        | 200000 | 收入 |
      And 不應觸發 CashPosition 同步
