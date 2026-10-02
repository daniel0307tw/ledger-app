# stock_analyzer

第三方系統（使用者自己的另一套股票交易記錄與分析系統，部署於同一台伺服器）。合法 Actor：外部第三方系統，非 ledger-app 內建邏輯。比照既有 Actor「Hermes」的模式——代表使用者呼叫 ledger-app 的 API 執行自動化操作。

## 描述
使用者在 stock_analyzer 手動輸入/編輯/刪除股票交易時，若歸屬券商可對應現金帳戶（永豐證券/新光證券），
stock_analyzer 會即時（同步 HTTP push）呼叫 ledger-app 的 API，建立/更新/刪除對應的記帳交易，
讓記帳系統的現金餘額反映股票交易造成的現金流動。

## 關鍵屬性
- 與「使用者」是不同 Actor：使用者是人類操作者（透過 ledger-app 前端 UI），stock_analyzer 是第三方系統（透過 API）
- 與「Hermes」是不同 Actor：Hermes 代表使用者做瀏覽器自動化（雲端發票），stock_analyzer 是使用者另一套獨立系統（股票交易記錄），兩者互不相關
- 比照既有 API 慣例，無認證層，靠網路邊界（僅同一台伺服器內部，127.0.0.1）做保護
- stock_analyzer 同時也是 ledger-app 的 API **消費端**（另一個既有的唯讀方向：ledger-app 讀取
  stock_analyzer 的持倉市值，見 stock_analyzer 的 `/api/portfolio/holdings`）；本 Activity 描述的是
  相反方向——stock_analyzer 主動呼叫 ledger-app
