import base64
import hashlib
import hmac
import json
import secrets
import struct
import time
from urllib.parse import quote

from .models import MultiFactorDevice
from .security import token_hash
from ..crypto.fields import decrypt_field, encrypt_field


def generate_totp_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode("utf-8").rstrip("=")


def _normalize_secret(secret: str) -> bytes:
    padding = "=" * ((8 - len(secret) % 8) % 8)
    return base64.b32decode((secret + padding).upper())


def _hotp(secret: str, counter: int, digits: int = 6) -> str:
    digest = hmac.new(_normalize_secret(secret), struct.pack(">Q", counter), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF
    return str(code % (10**digits)).zfill(digits)


def totp_code(secret: str, for_time: int | None = None, interval: int = 30, digits: int = 6) -> str:
    timestamp = int(for_time if for_time is not None else time.time())
    return _hotp(secret, timestamp // interval, digits)


def verify_totp_code(secret: str, code: str, *, window: int = 1, interval: int = 30, digits: int = 6) -> bool:
    normalized = "".join(char for char in code if char.isdigit())
    if len(normalized) != digits:
        return False
    counter = int(time.time()) // interval
    for offset in range(-window, window + 1):
        if hmac.compare_digest(_hotp(secret, counter + offset, digits), normalized):
            return True
    return False


def otpauth_uri(*, issuer: str, email: str, secret: str) -> str:
    label = quote(f"{issuer}:{email}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits=6&period=30"


def encrypted_secret(secret: str) -> str:
    encrypted = encrypt_field(secret)
    if encrypted is None:
        raise ValueError("MFA secret encryption failed")
    return encrypted


def decrypted_secret(device: MultiFactorDevice) -> str:
    decrypted = decrypt_field(device.secret_encrypted)
    if decrypted is None:
        raise ValueError("MFA secret decryption failed")
    return decrypted


def generate_recovery_codes(count: int = 8) -> list[str]:
    return [f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}" for _ in range(count)]


def recovery_code_hashes(codes: list[str]) -> str:
    return json.dumps([token_hash(code.strip().upper()) for code in codes], sort_keys=True)


def consume_recovery_code(device: MultiFactorDevice, code: str) -> bool:
    if not device.recovery_codes_hash:
        return False
    hashes: list[str] = json.loads(device.recovery_codes_hash)
    candidate = token_hash(code.strip().upper())
    for index, stored_hash in enumerate(hashes):
        if hmac.compare_digest(stored_hash, candidate):
            del hashes[index]
            device.recovery_codes_hash = json.dumps(hashes, sort_keys=True)
            return True
    return False
