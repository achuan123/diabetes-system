import base64
import hashlib

from cryptography.fernet import Fernet


def _fernet_key(secret: str) -> bytes:
    digest = hashlib.sha256(secret.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)


def get_cipher(config) -> Fernet:
    key = config.get('MEDICAL_ENCRYPTION_KEY') or _fernet_key(config['SECRET_KEY']).decode('utf-8')
    return Fernet(key.encode('utf-8'))


def encrypt_text(config, value: str | None) -> str | None:
    if value in (None, ''):
        return value
    return get_cipher(config).encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt_text(config, value: str | None) -> str | None:
    if value in (None, ''):
        return value
    return get_cipher(config).decrypt(value.encode('utf-8')).decode('utf-8')
