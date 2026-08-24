from app.models.category import CategoryType

DEFAULT_CATEGORIES = [
    ("餐飲", CategoryType.EXPENSE),
    ("日常用品", CategoryType.EXPENSE),
    ("交通", CategoryType.EXPENSE),
    ("水電瓦斯", CategoryType.EXPENSE),
    ("電話網路", CategoryType.EXPENSE),
    ("居家", CategoryType.EXPENSE),
    ("服飾", CategoryType.EXPENSE),
    ("汽車", CategoryType.EXPENSE),
    ("娛樂", CategoryType.EXPENSE),
    ("美容美髮", CategoryType.EXPENSE),
    ("交際應酬", CategoryType.EXPENSE),
    ("學習深造", CategoryType.EXPENSE),
    ("保險", CategoryType.EXPENSE),
    ("稅金", CategoryType.EXPENSE),
    ("醫療", CategoryType.EXPENSE),
    ("校正回歸", CategoryType.BOTH),
    ("轉帳手續費", CategoryType.EXPENSE),
    ("薪資", CategoryType.INCOME),
    ("獎金", CategoryType.INCOME),
    ("投資", CategoryType.INCOME),
]
