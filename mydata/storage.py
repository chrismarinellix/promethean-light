"""Encrypted storage for files and embeddings"""

import pickle
import hashlib
from pathlib import Path
from typing import Any, Optional, List
from .crypto import CryptoManager


class EncryptedStorage:
    """Handles encrypted file and embedding storage"""

    def __init__(self, crypto: CryptoManager, storage_dir: Optional[Path] = None):
        self.crypto = crypto
        self.storage_dir = storage_dir or (crypto.data_dir / "storage")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.files_dir = self.storage_dir / "files"
        self.embeddings_dir = self.storage_dir / "embeddings"
        self.files_dir.mkdir(exist_ok=True)
        self.embeddings_dir.mkdir(exist_ok=True)

    def write_file(self, file_id: str, data: bytes) -> Path:
        """Write encrypted file to storage"""
        encrypted = self.crypto.encrypt(data)
        file_path = self.files_dir / f"{file_id}.enc"
        file_path.write_bytes(encrypted)
        return file_path

    def read_file(self, file_id: str) -> bytes:
        """Read and decrypt file from storage"""
        file_path = self.files_dir / f"{file_id}.enc"
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_id}")
        encrypted = file_path.read_bytes()
        return self.crypto.decrypt(encrypted)

    def file_exists(self, file_id: str) -> bool:
        """Check if file exists in storage"""
        return (self.files_dir / f"{file_id}.enc").exists()

    def compute_hash(self, data: bytes) -> str:
        """Compute SHA-256 hash of data"""
        return hashlib.sha256(data).hexdigest()

    def encrypt_embedding(self, embedding: List[float]) -> bytes:
        """Encrypt an embedding vector"""
        pickled = pickle.dumps(embedding)
        return self.crypto.encrypt(pickled)

    def decrypt_embedding(self, encrypted_data: bytes) -> List[float]:
        """Decrypt an embedding vector"""
        decrypted = self.crypto.decrypt(encrypted_data)
        return pickle.loads(decrypted)

    def write_embedding(self, embedding_id: str, embedding: List[float]) -> Path:
        """Write encrypted embedding to storage"""
        encrypted = self.encrypt_embedding(embedding)
        emb_path = self.embeddings_dir / f"{embedding_id}.emb"
        emb_path.write_bytes(encrypted)
        return emb_path

    def read_embedding(self, embedding_id: str) -> List[float]:
        """Read and decrypt embedding from storage"""
        emb_path = self.embeddings_dir / f"{embedding_id}.emb"
        if not emb_path.exists():
            raise FileNotFoundError(f"Embedding not found: {embedding_id}")
        encrypted = emb_path.read_bytes()
        return self.decrypt_embedding(encrypted)
