"""License plate encryption/decryption using Fernet symmetric encryption."""

from cryptography.fernet import Fernet

from app.config import settings


def _get_fernet() -> Fernet:
    return Fernet(settings.encryption_key.encode())


def encrypt_license_plate(plaintext: str) -> str:
    """Encrypt a license plate string. Returns base64-encoded ciphertext."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt_license_plate(ciphertext: str) -> str:
    """Decrypt a license plate string from base64-encoded ciphertext."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()


def mask_license_plate(plaintext: str) -> str:
    """Mask a license plate for display: show first 2 and last 1 chars.

    Example: ABC-1234 -> AB****4
    """
    clean = plaintext.replace("-", "").replace(" ", "")
    if len(clean) <= 3:
        return clean[0] + "*" * (len(clean) - 1) if clean else ""
    return clean[:2] + "*" * (len(clean) - 3) + clean[-1]
