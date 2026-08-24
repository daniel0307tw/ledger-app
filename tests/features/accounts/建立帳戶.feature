@command
Feature: 帳戶 — 建立帳戶
  作為 使用者
  我要 建立一個帳戶
  以便 記錄不同來源（現金、銀行帳戶等）的收支

  # specs/features/系統抽象.md, specs/features/accounts/句型.md, specs/erm.dbml

  Rule: 前置（參數）- 帳戶名稱必須提供，且為使用者自訂字串，不限定於預先定義的類型清單

    Example: 缺少帳戶名稱時操作失敗
      When 使用者建立帳戶：
        | name | type     |
        |      | 一般帳戶 |
      Then 操作失敗，錯誤為"必要參數未提供"

  Rule: 前置（參數）- 帳戶類型必須提供，值為「一般帳戶」或「信用卡」

    Example: 缺少帳戶類型時操作失敗
      When 使用者建立帳戶：
        | name     | type |
        | 永豐銀行 |      |
      Then 操作失敗，錯誤為"必要參數未提供"

  Rule: 後置（狀態）- 建立後應新增一個帳戶

    Example: 建立後應新增一個帳戶
      When 使用者建立帳戶：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
      Then 操作成功，結果符合：
        | name     | type     |
        | 永豐銀行 | 一般帳戶 |
