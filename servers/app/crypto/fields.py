import base64
import hashlib
from cryptography.fernet import Fernet
from ..config import get_settings


def _fernet() -> Fernet:
    settings = get_settings()
    source = settings.field_encryption_key or settings.jwt_secret_key
    digest = hashlib.sha256(source.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_field(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_field(value: str | None) -> str | None:
    if value is None:
        return None
    return _fernet().decrypt(value.encode("utf-8")).decode("utf-8")
