class BusinessError(Exception):
    """業務規則不滿足（前置狀態驗證失敗，但不是資源不存在）。對應 HTTP 422。"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(Exception):
    """引用的資源不存在。對應 HTTP 404。"""

    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(message)


class InvalidParameterError(Exception):
    """參數缺少或格式錯誤（含跨欄位的參數驗證，如日期區間顛倒）。對應 HTTP 400。"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
