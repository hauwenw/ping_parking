import re


def validate_taiwan_phone(phone: str) -> str:
    """Validate Taiwan mobile phone: 09XXXXXXXX (10 digits)."""
    if not re.match(r"^09\d{8}$", phone):
        raise ValueError("手機號碼格式錯誤，請輸入09開頭的10碼號碼")
    return phone


def format_phone_display(phone: str) -> str:
    """Format phone for display: 0912345678 → 0912-345-678."""
    if len(phone) != 10:
        return phone
    return f"{phone[:4]}-{phone[4:7]}-{phone[7:]}"
