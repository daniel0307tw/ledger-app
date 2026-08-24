# Hermes

第三方 AI agent 系統（NousResearch hermes-agent，部署於使用者自己管理的伺服器），代表使用者呼叫 ledger-app 的 API 執行自動化操作。合法 Actor：外部第三方系統，非 ledger-app 內建邏輯。

## 描述
Hermes 定期（透過自己的排程機制）用瀏覽器自動化登入財政部電子發票整合服務平台，抓取使用者手機條碼載具下累積的雲端發票，整理成結構化資料後呼叫 ledger-app 的 API，把新發票同步成收支紀錄。抓取/登入本身不在 ledger-app 的規格範圍內，Hermes 只是這個 Activity 裡「呼叫 API 的外部系統」。

## 關鍵屬性
- 與「使用者」是不同 Actor：使用者是人類操作者（透過 UI），Hermes 是代表使用者運作的第三方系統（透過 API）
- Hermes 本身沒有身份驗證機制呼叫 ledger-app（比照既有 API 慣例，無認證層，靠網路邊界（僅 127.0.0.1）做保護）
- Hermes 也是既有 receipt-auto-ledger skill（收據照片自動記帳）的呼叫端，此為同一個 Actor 的第二種操作
