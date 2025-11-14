"""Encryption primitives for MyData"""

import os
import base64
import getpass
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoManager:
    """Handles all encryption/decryption operations"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or Path.home() / ".mydata"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.key_file = self.data_dir / "master.key"
        self.salt_file = self.data_dir / "salt.bin"
        self._fernet = None

    def setup(self, passphrase: Optional[str] = None) -> None:
        """Initialize master key with passphrase"""
        if self.key_file.exists():
            raise FileExistsError(
                f"Master key already exists at {self.key_file}. "
                "Delete it first to re-initialize."
            )

        if passphrase is None:
            passphrase = getpass.getpass("Enter master passphrase: ")
            passphrase2 = getpass.getpass("Re-enter passphrase: ")
            if passphrase != passphrase2:
                raise ValueError("Passphrases do not match")

        # Generate random salt
        salt = os.urandom(32)
        self.salt_file.write_bytes(salt)

        # Derive key and save (encrypted with itself - bootstrap)
        key = self._derive_key(passphrase, salt)
        fernet = Fernet(key)
        encrypted_salt = fernet.encrypt(salt)
        self.key_file.write_bytes(encrypted_salt)

        # Secure permissions (Unix-like)
        try:
            os.chmod(self.key_file, 0o600)
            os.chmod(self.salt_file, 0o600)
        except Exception:
            pass  # Windows doesn't support chmod

        print(f"✓ Master key created: {self.key_file}")

    def unlock(self, passphrase: Optional[str] = None) -> None:
        """Unlock with passphrase and cache Fernet instance"""
        if not self.key_file.exists():
            raise FileNotFoundError(
                f"No master key found at {self.key_file}. Run 'mydata setup' first."
            )

        if passphrase is None:
            passphrase = os.environ.get("MYDATA_PASSPHRASE") or getpass.getpass(
                "Master passphrase: "
            )

        # Load salt
        salt = self.salt_file.read_bytes()

        # Derive key
        key = self._derive_key(passphrase, salt)
        fernet = Fernet(key)

        # Verify by decrypting the stored salt
        try:
            encrypted_salt = self.key_file.read_bytes()
            fernet.decrypt(encrypted_salt)
        except Exception:
            raise ValueError("Incorrect passphrase")

        self._fernet = fernet

    def _derive_key(self, passphrase: str, salt: bytes) -> bytes:
        """Derive encryption key from passphrase using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=600_000,  # OWASP recommendation 2023
        )
        key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
        return key

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data"""
        if self._fernet is None:
            raise RuntimeError("CryptoManager not unlocked. Call unlock() first.")
        return self._fernet.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data"""
        if self._fernet is None:
            raise RuntimeError("CryptoManager not unlocked. Call unlock() first.")
        return self._fernet.decrypt(encrypted_data)

    def encrypt_str(self, text: str) -> bytes:
        """Encrypt string"""
        return self.encrypt(text.encode())

    def decrypt_str(self, encrypted_data: bytes) -> str:
        """Decrypt to string"""
        return self.decrypt(encrypted_data).decode()

    @property
    def is_unlocked(self) -> bool:
        """Check if crypto manager is unlocked"""
        return self._fernet is not None
