@query
Feature: 查詢待確認雲端發票清單

  Background:
    Given 系統中有以下雲端發票同步紀錄：
      | invoice_number | invoice_date | amount | seller_name  | status         |
      | AB-11111111     | 2026-08-19   | 200    | 全家便利商店 | pending_review |
      | AB-22222222     | 2026-08-18   | 500    | 家樂福       | synced         |
      | AB-33333333     | 2026-08-17   | 80     | 萊爾富       | skipped        |

  Rule: 後置（回應）- 查詢結果應只包含 pending_review 狀態的發票，已建立(synced)或已略過(skipped)的不列入

    Example: 查詢結果只列出待確認狀態的發票
      When 使用者查詢待確認雲端發票清單
      Then 操作成功，查詢結果應包含以下待確認發票：
        | invoice_number | invoice_date | amount | seller_name  |
        | AB-11111111     | 2026-08-19   | 200    | 全家便利商店 |

  Rule: 後置（回應）- 每筆待確認發票應附上與其相似的既有交易資訊，供使用者比對判斷是否為同一筆消費
