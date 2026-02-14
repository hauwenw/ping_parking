from uuid import UUID


class BusinessError(Exception):
    """Base class for business logic errors."""

    def __init__(self, message: str, code: str = "BUSINESS_ERROR") -> None:
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(BusinessError):
    def __init__(self, entity: str, entity_id: UUID | str) -> None:
        super().__init__(f"找不到{entity} (ID: {entity_id})", "NOT_FOUND")


class DuplicateError(BusinessError):
    def __init__(self, entity: str, field: str, value: str) -> None:
        super().__init__(f"{entity}的{field}「{value}」已存在", "DUPLICATE")


class DoubleBookingError(BusinessError):
    def __init__(self, space_name: str) -> None:
        super().__init__(
            f"車位「{space_name}」已有有效合約，無法重複分配", "DOUBLE_BOOKING"
        )


class AuthenticationError(BusinessError):
    def __init__(self) -> None:
        super().__init__("電子郵件或密碼錯誤，請重試", "AUTH_FAILED")


class UnauthorizedError(BusinessError):
    def __init__(self) -> None:
        super().__init__("無效的認證令牌", "UNAUTHORIZED")
