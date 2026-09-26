import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.crypto.key_derivation import derive_key


def encrypt_data(
    data: bytes,
    password: str
) -> dict:

    salt = os.urandom(16)

    key = derive_key(
        password=password,
        salt=salt
    )

    nonce = os.urandom(12)

    aesgcm = AESGCM(key)

    ciphertext = aesgcm.encrypt(
        nonce,
        data,
        None
    )

    return {
        "salt": salt,
        "nonce": nonce,
        "ciphertext": ciphertext
    }


def decrypt_data(
    salt: bytes,
    nonce: bytes,
    ciphertext: bytes,
    password: str
) -> bytes:

    key = derive_key(
        password=password,
        salt=salt
    )

    aesgcm = AESGCM(key)

    plaintext = aesgcm.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext