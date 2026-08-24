@command
Feature: 處理待確認雲端發票

  Background:
    Given 系統中有以下帳戶：
      | id | name | type   |
      | 5  | 現金 | 一般帳戶 |

  Rule: 前置（狀態）- 只有 pending_review 狀態的發票可以被處理，已是 synced 或 skipped 的操作應失敗

    Example: 已處理過的發票再次處理時操作失敗
      Given 系統中有以下雲端發票同步紀錄：
        | invoice_number | invoice_date | amount | seller_name | status |
        | AB-77777777     | 2026-08-15   | 90     | 全聯       | synced |
      When 使用者將編號 AB-77777777 的待確認發票標記為"確認為新交易"
      Then 操作失敗，錯誤為"此筆發票已處理過"

  Rule: 後置（狀態）- 使用者選擇「確認為新交易」時，應建立一筆支出交易並將發票狀態改為 synced（帳戶/分類可由使用者於確認時指定，未指定則沿用「同步雲端發票」的預設邏輯：現金帳戶、日常用品分類）  # 設計依據：比照既有 create-transaction 需要 accountId/categoryId 的慣例，允許確認時覆寫，未指定則沿用自動記帳的既有預設

    Example: 確認為新交易時建立支出交易並更新狀態
      Given 系統中有以下雲端發票同步紀錄：
        | invoice_number | invoice_date | amount | seller_name | status         |
        | AB-55555555     | 2026-08-21   | 500    | 鼎泰豐       | pending_review |
      When 使用者將編號 AB-55555555 的待確認發票標記為"確認為新交易"
      Then 操作成功，該筆發票狀態應變為"synced"
      And 操作成功，應建立一筆支出交易，帳戶為"現金"、分類為"日常用品"、金額為 500

  Rule: 後置（狀態）- 使用者選擇「這是重複的（已手動記過）」時，發票狀態應改為 skipped，不建立交易

    Example: 確認為重複時只更新狀態不建立交易
      Given 系統中有以下雲端發票同步紀錄：
        | invoice_number | invoice_date | amount | seller_name | status         |
        | AB-66666666     | 2026-08-20   | 300    | 星巴克       | pending_review |
      When 使用者將編號 AB-66666666 的待確認發票標記為"確認為重複"
      Then 操作成功，該筆發票狀態應變為"skipped"
