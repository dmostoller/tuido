"""End-to-end encryption for cloud sync.

This module provides AES-256-GCM encryption with Argon2id key derivation
for securing sync data before upload to the cloud.
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Optional

import keyring

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

logger = logging.getLogger(__name__)

# Keyring service name for storing credentials
KEYRING_SERVICE = "tuido"
KEYRING_KEY = "encryption_password"
KEYRING_DEVICE_TOKEN = "device_token"
KEYRING_DEVICE_ID = "device_id"


@dataclass
class EncryptedPayload:
    """Encrypted data with metadata for decryption."""

    version: int
    algorithm: str
    kdf: str
    salt: str  # Base64
    nonce: str  # Base64
    ciphertext: str  # Base64
    tag: str  # Base64

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "algorithm": self.algorithm,
            "kdf": self.kdf,
            "salt": self.salt,
            "nonce": self.nonce,
            "ciphertext": self.ciphertext,
            "tag": self.tag,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EncryptedPayload":
        """Create from dictionary."""
        return cls(
            version=data["version"],
            algorithm=data["algorithm"],
            kdf=data["kdf"],
            salt=data["salt"],
            nonce=data["nonce"],
            ciphertext=data["ciphertext"],
            tag=data["tag"],
        )


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive 256-bit encryption key from password using Argon2id.

    Args:
        password: User's encryption password
        salt: 16-byte random salt

    Returns:
        32-byte encryption key
    """
    kdf = Argon2id(
        salt=salt,
        length=32,  # 256 bits
        iterations=3,  # Time cost
        lanes=4,  # Parallelism
        memory_cost=65536,  # 64 MB
    )
    return kdf.derive(password.encode())


def encrypt_data(plaintext: str, password: str) -> EncryptedPayload:
    """Encrypt data using AES-256-GCM.

    Args:
        plaintext: JSON string to encrypt
        password: User's encryption password

    Returns:
        EncryptedPayload with all metadata needed for decryption

    Raises:
        ValueError: If password or plaintext is empty
    """
    if not password:
        raise ValueError("Encryption password cannot be empty")
    if not plaintext:
        raise ValueError("Cannot encrypt empty data")

    # Generate random salt and nonce
    salt = os.urandom(16)
    nonce = os.urandom(12)  # 96 bits for GCM

    # Derive key from password
    key = derive_key(password, salt)

    # Encrypt with AES-256-GCM
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext.encode(), None)

    # GCM appends 16-byte tag to ciphertext
    ciphertext = ciphertext_with_tag[:-16]
    tag = ciphertext_with_tag[-16:]

    return EncryptedPayload(
        version=1,
        algorithm="aes-256-gcm",
        kdf="argon2id",
        salt=base64.b64encode(salt).decode(),
        nonce=base64.b64encode(nonce).decode(),
        ciphertext=base64.b64encode(ciphertext).decode(),
        tag=base64.b64encode(tag).decode(),
    )


def decrypt_data(payload: EncryptedPayload, password: str) -> str:
    """Decrypt data using AES-256-GCM.

    Args:
        payload: Encrypted payload from server
        password: User's encryption password

    Returns:
        Decrypted JSON string

    Raises:
        ValueError: If password is empty
        cryptography.exceptions.InvalidTag: If password is wrong or data tampered
    """
    if not password:
        raise ValueError("Decryption password cannot be empty")

    # Decode base64 values
    salt = base64.b64decode(payload.salt)
    nonce = base64.b64decode(payload.nonce)
    ciphertext = base64.b64decode(payload.ciphertext)
    tag = base64.b64decode(payload.tag)

    # Derive key from password
    key = derive_key(password, salt)

    # Decrypt with AES-256-GCM
    aesgcm = AESGCM(key)
    ciphertext_with_tag = ciphertext + tag
    plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)

    return plaintext.decode()


def get_encryption_password() -> Optional[str]:
    """Get encryption password from system keyring.

    Returns:
        Password string if set, None otherwise
    """
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_KEY)
    except Exception as e:
        logger.warning("Failed to get encryption password from keyring: %s: %s", type(e).__name__, e)
        return None


def set_encryption_password(password: str) -> bool:
    """Store encryption password in system keyring.

    Args:
        password: Password to store

    Returns:
        True if successful, False otherwise
    """
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_KEY, password)
        return True
    except Exception as e:
        logger.warning("Failed to set encryption password in keyring: %s: %s", type(e).__name__, e)
        return False


def delete_encryption_password() -> bool:
    """Remove encryption password from system keyring.

    Returns:
        True if successful, False otherwise
    """
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_KEY)
        return True
    except Exception as e:
        logger.warning("Failed to delete encryption password from keyring: %s: %s", type(e).__name__, e)
        return False


def has_encryption_password() -> bool:
    """Check if encryption password is set.

    Returns:
        True if password exists in keyring
    """
    return get_encryption_password() is not None


# =============================================================================
# Device Token Storage (for device authorization flow)
# =============================================================================


def get_device_token() -> Optional[str]:
    """Get device token from system keyring.

    Returns:
        Token string if set, None otherwise
    """
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_DEVICE_TOKEN)
    except Exception as e:
        logger.warning("Failed to get device token from keyring: %s: %s", type(e).__name__, e)
        return None


def get_device_id() -> Optional[str]:
    """Get device ID from system keyring.

    Returns:
        Device ID if set, None otherwise
    """
    try:
        return keyring.get_password(KEYRING_SERVICE, KEYRING_DEVICE_ID)
    except Exception as e:
        logger.warning("Failed to get device ID from keyring: %s: %s", type(e).__name__, e)
        return None


def save_device_credentials(token: str, device_id: str) -> bool:
    """Store device token and ID in system keyring.

    Args:
        token: Device token from authorization
        device_id: Device ID from authorization

    Returns:
        True if successful, False otherwise
    """
    try:
        keyring.set_password(KEYRING_SERVICE, KEYRING_DEVICE_TOKEN, token)
        keyring.set_password(KEYRING_SERVICE, KEYRING_DEVICE_ID, device_id)
        return True
    except Exception as e:
        logger.warning("Failed to save device credentials to keyring: %s: %s", type(e).__name__, e)
        return False


def delete_device_credentials() -> bool:
    """Remove device credentials from system keyring.

    Returns:
        True if both credentials were deleted successfully, False otherwise
    """
    token_deleted = True
    device_id_deleted = True
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_DEVICE_TOKEN)
    except Exception:
        token_deleted = False
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_DEVICE_ID)
    except Exception:
        device_id_deleted = False
    return token_deleted and device_id_deleted


def has_device_token() -> bool:
    """Check if device is linked (has token).

    Returns:
        True if device token exists in keyring
    """
    return get_device_token() is not None
