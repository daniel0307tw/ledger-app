@command
Feature: 同步雲端發票

  Background:
    Given 系統中有以下帳戶：
      | id | name | type   |
      | 5  | 現金 | 一般帳戶 |

  Rule: 前置（參數）- 每筆發票資料必須包含發票字軌+號碼、日期、總金額、賣方名稱

    Example: 批次中有一筆缺必要欄位時，該筆標示資料錯誤，不影響其他筆
      Given 系統中無其他既有雲端發票紀錄
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name |
        | AB-33333333     | 2026-08-20   | 100    | 好市多       |
        | AB-44444444     | 2026-08-20   |        | 家樂福       |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果     |
        | AB-33333333     | 已建立   |
        | AB-44444444     | 資料錯誤 |

  Rule: 前置（狀態）- 發票字軌+號碼已同步過時，該筆應被略過，不重複建立交易

    Example: 發票號碼已同步過時應略過
      Given 系統中有以下雲端發票同步紀錄：
        | invoice_number | invoice_date | amount | seller_name | status |
        | AB-11111111     | 2026-08-19   | 200    | 全家便利商店 | synced |
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name |
        | AB-11111111     | 2026-08-19   | 200    | 全家便利商店 |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果   |
        | AB-11111111     | 已略過 |

  Rule: 前置（狀態）- 發票字軌+號碼未同步過，但金額與日期與既有交易相似時，該筆應標記為 pending_review 狀態並存入 cloud_invoice 表，不自動建立交易（後續由「處理待確認雲端發票」功能解決，見同 domain 另一 Feature）

    Example: 金額日期與既有交易相似時標記為待確認
      Given 系統中有以下收支紀錄：
        | id | date       | amount | category | account | type |
        | 1  | 2026-08-20 | 300    | 日常用品 | 現金    | 支出 |
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name |
        | AB-22222222     | 2026-08-20   | 300    | 鼎泰豐       |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果   |
        | AB-22222222     | 待確認 |

  Rule: 後置（狀態）- 發票字軌+號碼未同步過且與既有交易不相似時，應自動建立一筆支出交易，帳戶預設為「現金」

    Example: 無相似交易時自動建立支出交易
      Given 系統中無其他既有雲端發票紀錄與收支紀錄
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name  |
        | AB-11111111     | 2026-08-20   | 150    | 全家便利商店 |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果   |
        | AB-11111111     | 已建立 |
      And 操作成功，應建立一筆支出交易，帳戶為"現金"、分類為"日常用品"、金額為 150

  Rule: 後置（狀態）- 自動建立交易時，依賣方名稱與品項摘要嘗試以關鍵字判斷分類；比對到高信心的分類則直接採用，不理會 Hermes 提供的建議分類

    Example: 賣方/品項含餐飲關鍵字時自動歸類為餐飲，不落入日常用品
      Given 系統中無其他既有雲端發票紀錄與收支紀錄
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name | item_summary |
        | AB-55555555     | 2026-08-20   | 1287   | 貓禾咖啡店   | 古法肉醬寬扁麵、B套餐 |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果   |
        | AB-55555555     | 已建立 |
      And 操作成功，應建立一筆支出交易，帳戶為"現金"、分類為"餐飲"、金額為 1287

    Example: 賣方/品項含交通關鍵字時自動歸類為交通
      Given 系統中無其他既有雲端發票紀錄與收支紀錄
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name         | item_summary |
        | AB-66666666     | 2026-08-19   | 1270   | 南強加油站實業有限公司 | 九五無鉛汽油 |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果   |
        | AB-66666666     | 已建立 |
      And 操作成功，應建立一筆支出交易，帳戶為"現金"、分類為"交通"、金額為 1270

  Rule: 後置（狀態）- 關鍵字比對不到分類、但 Hermes 有提供建議分類時，採用該建議分類

    Example: 關鍵字比對不到分類時採用 Hermes 建議分類
      Given 系統中無其他既有雲端發票紀錄與收支紀錄
      When Hermes 傳送以下雲端發票資料進行同步：
        | invoice_number | invoice_date | amount | seller_name | 建議分類 |
        | AB-77777777     | 2026-08-10   | 149    | 三友藥妝     | 美容美髮 |
      Then 操作成功，同步結果應包含以下逐筆處理：
        | invoice_number | 結果   |
        | AB-77777777     | 已建立 |
      And 操作成功，應建立一筆支出交易，帳戶為"現金"、分類為"美容美髮"、金額為 149

  Rule: 後置（狀態）- 關鍵字比對不到分類、Hermes 也沒有提供建議分類時，預設歸類為「日常用品」（category_id 為必填欄位，不可留空）

  Rule: 後置（狀態）- 自動建立交易後，應將該筆發票字軌+號碼記錄為已同步（status=synced），避免下次重複處理

  Rule: 後置（狀態）- 批次中每筆發票獨立處理，單筆資料缺必要欄位不影響其餘筆數的處理結果  # 設計依據：批次 API 常見慣例為逐筆獨立處理，且使用者未提及「全部失敗」語意，採較寬鬆的逐筆隔離設計

  Rule: 後置（回應）- 操作應回傳這批發票逐筆的處理結果（已建立/待確認/已略過/資料錯誤）
