"""依賣方名稱／品項摘要做關鍵字比對，推測雲端發票自動同步交易應歸類的分類。

關鍵字清單刻意保守，只收錄高信心、不容易跟其他分類混淆的型態——寧可比對不到（回傳
None，交由呼叫端走 Hermes 建議分類或預設分類的後備順序），也不要亂猜造成新的誤判。
之後若發現新的常見誤判型態（例如某類賣方名稱一直被分錯），把對應關鍵字補進下面的清單即可，
不需要更動呼叫端邏輯。
"""

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "餐飲": [
        "咖啡", "茶飲", "飲料", "小吃", "拉麵", "火鍋", "燒肉", "壽司", "便當",
        "居酒屋", "餐廳", "Food Court", "鍋貼", "水餃", "飯糰", "吐司", "螺螄粉",
        "麵包", "蛋糕", "早餐", "宵夜", "熱炒", "涼麵", "滷味", "鹹酥雞", "炸雞",
        "飲", "茶",
    ],
    "交通": [
        "加油站", "停車場", "Parking", "停車費", "無鉛汽油", "悠遊卡", "高鐵",
        "台鐵", "計程車", "Uber",
    ],
    "娛樂": [
        "影城", "電影", "訂票", "KTV", "美術館", "博物館", "遊樂園", "當代藝術館",
    ],
}


def classify_category(seller_name: str, item_summary: str | None) -> str | None:
    """回傳判斷出的分類名稱；沒有任何關鍵字命中則回傳 None（不代表分類是空的，
    只代表這個分類器沒有信心判斷，呼叫端應該接著嘗試其他後備來源）。"""
    haystack = f"{seller_name} {item_summary or ''}"
    for category_name, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in haystack for keyword in keywords):
            return category_name
    return None
