import base64

from cryptography.fernet import Fernet


def get_cipher(config) -> Fernet:
    key = config.get('MEDICAL_ENCRYPTION_KEY')
    if not key:
        raise RuntimeError('MEDICAL_ENCRYPTION_KEY must be configured')
    return Fernet(key.encode('utf-8'))


def encrypt_text(config, value: str | None) -> str | None:
    if value in (None, ''):
        return value
    return get_cipher(config).encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt_text(config, value: str | None) -> str | None:
    if value in (None, ''):
        return value
    return get_cipher(config).decrypt(value.encode('utf-8')).decode('utf-8')
