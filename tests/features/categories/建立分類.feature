@command
Feature: 分類 — 建立分類
  作為 使用者
  我要 建立一個分類
  以便 記帳時能歸類收支，供未來報表依分類統計

  # specs/features/系統抽象.md, specs/features/categories/句型.md, specs/erm.dbml

  Rule: 前置（參數）- 分類名稱必須提供，且為使用者自訂字串，不要求與既有分類不同（可重複）

    Example: 缺少分類名稱時操作失敗
      When 使用者建立分類：
        | name | type |
        |      | 支出 |
      Then 操作失敗，錯誤為"必要參數未提供"

  Rule: 前置（參數）- 收支類型必須提供，值為「收入」「支出」或「皆可」

    Example: 缺少收支類型時操作失敗
      When 使用者建立分類：
        | name   | type |
        | 健身房 |      |
      Then 操作失敗，錯誤為"必要參數未提供"

  Rule: 後置（狀態）- 建立後應新增一個分類

    Example: 建立後應新增一個分類
      When 使用者建立分類：
        | name   | type |
        | 健身房 | 支出 |
      Then 操作成功，結果符合：
        | name   | type |
        | 健身房 | 支出 |
