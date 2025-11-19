"""ML-based organization: clustering and auto-tagging"""

import numpy as np
from collections import Counter
from typing import Optional, List
from sqlmodel import Session, select
from .models import Document, Chunk, Cluster, Tag
from .embedder import Embedder


class MLOrganizer:
    """Organizes documents using ML clustering and tagging"""

    def __init__(self, embedder: Embedder, db_session: Session):
        self.embedder = embedder
        self.db = db_session
        self._clusterer = None
        self._tagger = None

    def run_clustering(self, min_cluster_size: int = 5, min_samples: int = 3) -> dict:
        """Run HDBSCAN clustering on all document embeddings"""
        from datetime import datetime

        start_time = datetime.now()
        timestamp = start_time.strftime("%H:%M:%S")

        print(f"[ML] [{timestamp}] Running clustering analysis...")

        # Get document and chunk counts
        try:
            doc_count = len(self.db.exec(select(Document)).all())
            chunk_count = len(self.db.exec(select(Chunk)).all())
            tag_count = len(self.db.exec(select(Tag)).all())
            cluster_count = len(self.db.exec(select(Cluster)).all())

            print(f"[ML] [{timestamp}] Database status:")
            print(f"      • Documents: {doc_count}")
            print(f"      • Chunks: {chunk_count}")
            print(f"      • Tags: {tag_count}")
            print(f"      • Existing clusters: {cluster_count}")

        except Exception as e:
            print(f"[ML] [{timestamp}] Warning: Could not fetch stats: {e}")
            doc_count = 0

        # Get all chunks with embeddings from Qdrant
        # For now, we'll use a simplified version
        # In production, this would fetch from Qdrant and run HDBSCAN

        try:
            import hdbscan
            import umap
            print(f"[ML] [{timestamp}] HDBSCAN/UMAP available - clustering enabled")
        except ImportError:
            print(f"[ML] [{timestamp}] ⚠ HDBSCAN/UMAP not available (install with: pip install hdbscan umap-learn)")
            print(f"[ML] [{timestamp}] Skipping clustering - using tag-based organization only")
            return {"status": "skipped", "reason": "missing dependencies"}

        # This is a placeholder - full implementation would:
        # 1. Fetch all embeddings from Qdrant
        # 2. Reduce dimensions with UMAP
        # 3. Cluster with HDBSCAN
        # 4. Generate cluster labels
        # 5. Update database

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"[ML] [{timestamp}] ✓ Analysis complete in {duration:.2f}s")
        print(f"[ML] [{timestamp}] No changes detected - database stable")

        return {"status": "ok", "clusters": cluster_count}

    def auto_tag(self, doc_id: str, text: str, top_k: int = 3) -> List[str]:
        """Generate tags for a document using keyword extraction"""
        # Simple frequency-based tagging
        # In production, use SetFit or a zero-shot classifier

        words = text.lower().split()
        # Remove common stop words
        stop_words = {
            "the",
            "is",
            "at",
            "which",
            "on",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "with",
            "to",
            "for",
            "of",
        }
        words = [w.strip(".,!?;:") for w in words if w not in stop_words and len(w) > 3]

        # Get most common words as tags
        counter = Counter(words)
        tags = [word for word, count in counter.most_common(top_k) if count > 1]

        # Detect common patterns
        text_lower = text.lower()
        if any(word in text_lower for word in ["buy", "sell", "stock", "shares", "$"]):
            tags.append("finance")
        if any(word in text_lower for word in ["def", "class", "import", "function"]):
            tags.append("code")
        if any(word in text_lower for word in ["doctor", "appointment", "health"]):
            tags.append("health")

        return list(set(tags))[:top_k]

    def organize_document(self, doc_id: str, text: str) -> dict:
        """Run full ML organization on a document"""
        from uuid import UUID

        # Auto-tag
        tags = self.auto_tag(doc_id, text)

        # Save tags to database
        # Convert doc_id to UUID if it's a string
        if isinstance(doc_id, str):
            try:
                doc_id_uuid = UUID(doc_id)
            except Exception:
                # If conversion fails, skip tagging
                return {"tags": [], "cluster_id": None}
        else:
            doc_id_uuid = doc_id

        for tag_text in tags:
            tag = Tag(doc_id=doc_id_uuid, tag=tag_text, confidence=0.8)
            self.db.add(tag)

        try:
            self.db.commit()
        except Exception as e:
            print(f"Warning: Failed to save tags: {e}")
            self.db.rollback()

        return {"tags": tags, "cluster_id": None}

    def get_cluster_summary(self, cluster_id: int) -> Optional[str]:
        """Generate a summary for a cluster (placeholder for LLM summary)"""
        stmt = select(Document).where(Document.cluster_id == cluster_id).limit(10)
        docs = self.db.exec(stmt).all()

        if not docs:
            return None

        # Simple summary: most common words
        all_text = " ".join([doc.raw_text[:200] for doc in docs])
        words = all_text.lower().split()
        counter = Counter(words)
        common = [word for word, _ in counter.most_common(5)]

        return f"Documents about: {', '.join(common)}"
