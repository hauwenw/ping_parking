class BusinessError(Exception):
    """Base class for business logic errors."""

    def __init__(self, message: str, code: str = "BUSINESS_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(BusinessError):
    def __init__(self, entity: str) -> None:
        super().__init__(f"找不到{entity}", "NOT_FOUND")


class DuplicateError(BusinessError):
    def __init__(self, entity: str, field: str) -> None:
        super().__init__(f"{entity}的{field}已存在", "DUPLICATE")


class DoubleBookingError(BusinessError):
    def __init__(self, space_name: str) -> None:
        super().__init__(
            f"車位「{space_name}」已有有效合約，無法重複分配", "DOUBLE_BOOKING"
        )
