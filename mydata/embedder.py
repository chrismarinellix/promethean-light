"""Text embedding using sentence transformers"""

import os
from pathlib import Path
from typing import Optional, Union, List
import numpy as np


class Embedder:
    """Generates embeddings using local models"""

    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5", cache_dir: Optional[Path] = None):
        self.model_name = model_name
        self.cache_dir = cache_dir or Path.home() / ".mydata" / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Set cache directory for HuggingFace
        os.environ["TRANSFORMERS_CACHE"] = str(self.cache_dir)
        os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(self.cache_dir)

        self._model = None

    @property
    def model(self):
        """Lazy load model"""
        if self._model is None:
            print(f"Loading embedding model: {self.model_name}...")
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name, cache_folder=str(self.cache_dir))
                print(f"[OK] Model loaded: {self.model_name} ({self.dimension} dims)")
            except Exception as e:
                print(f"Error loading model: {e}")
                raise
        return self._model

    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.model.get_sentence_embedding_dimension()

    def embed(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embedding(s) for text"""
        return self.model.encode(text, show_progress_bar=False, convert_to_numpy=True)

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for batch of texts"""
        return self.model.encode(
            texts, show_progress_bar=True, batch_size=batch_size, convert_to_numpy=True
        )

    def similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings"""
        return float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))
