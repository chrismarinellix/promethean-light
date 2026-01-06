"""ML-based organization: clustering and auto-tagging"""

import numpy as np
from collections import Counter
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select
from .models import Document, Chunk, Cluster, Tag
from .embedder import Embedder


# Try to import clustering libraries
try:
    import hdbscan
    import umap
    CLUSTERING_AVAILABLE = True
except ImportError:
    CLUSTERING_AVAILABLE = False


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
        from sqlalchemy import func

        start_time = datetime.now()
        timestamp = start_time.strftime("%H:%M:%S")

        # Get document and chunk counts - OPTIMIZED with COUNT
        try:
            doc_count = self.db.scalar(select(func.count(Document.id)))
            chunk_count = self.db.scalar(select(func.count(Chunk.id)))
            tag_count = self.db.scalar(select(func.count(Tag.id)))
            cluster_count = self.db.scalar(select(func.count(Cluster.id)))

            # Track if there are changes since last run
            if not hasattr(self, '_last_doc_count'):
                self._last_doc_count = doc_count
                self._last_chunk_count = chunk_count
                self._last_tag_count = tag_count
                has_changes = True
            else:
                has_changes = (
                    doc_count != self._last_doc_count or
                    chunk_count != self._last_chunk_count or
                    tag_count != self._last_tag_count
                )

            # Only print details if there are changes
            if has_changes:
                print(f"[ML] [{timestamp}] Database activity detected:")

                if doc_count != self._last_doc_count:
                    diff = doc_count - self._last_doc_count
                    print(f"      • Documents: {doc_count} (+{diff})")
                else:
                    print(f"      • Documents: {doc_count}")

                if chunk_count != self._last_chunk_count:
                    diff = chunk_count - self._last_chunk_count
                    print(f"      • Chunks: {chunk_count} (+{diff})")
                else:
                    print(f"      • Chunks: {chunk_count}")

                if tag_count != self._last_tag_count:
                    diff = tag_count - self._last_tag_count
                    print(f"      • Tags: {tag_count} (+{diff})")
                else:
                    print(f"      • Tags: {tag_count}")

                print(f"      • Clusters: {cluster_count}")

                # Update last counts
                self._last_doc_count = doc_count
                self._last_chunk_count = chunk_count
                self._last_tag_count = tag_count

        except Exception as e:
            print(f"[ML] [{timestamp}] Warning: Could not fetch stats: {e}")
            doc_count = 0
            has_changes = False

        # Check if clustering is available
        if not CLUSTERING_AVAILABLE:
            if has_changes:
                print(f"[ML] [{timestamp}] Using tag-based organization (HDBSCAN/UMAP not installed)")
            return {"status": "skipped", "reason": "missing dependencies", "has_changes": has_changes}

        if has_changes:
            print(f"[ML] [{timestamp}] HDBSCAN/UMAP available - running clustering...")

        # Run clustering if there are enough documents AND (changes OR no clusters exist)
        needs_clustering = has_changes or cluster_count == 0
        if doc_count >= min_cluster_size and needs_clustering:
            if cluster_count == 0 and not has_changes:
                print(f"[ML] [{timestamp}] No clusters exist yet - running initial clustering...")
            try:
                new_clusters = self._perform_clustering(min_cluster_size, min_samples, timestamp)
                cluster_count = new_clusters
            except Exception as e:
                print(f"[ML] [{timestamp}] Clustering failed: {e}")
                import traceback
                traceback.print_exc()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        if has_changes:
            print(f"[ML] [{timestamp}] Analysis complete in {duration:.2f}s - {cluster_count} clusters")

        return {
            "status": "ok",
            "clusters": cluster_count,
            "has_changes": has_changes,
            "doc_count": doc_count,
            "chunk_count": chunk_count
        }

    def _perform_clustering(self, min_cluster_size: int, min_samples: int, timestamp: str) -> int:
        """Actually perform HDBSCAN clustering on document embeddings"""
        from sqlalchemy import func

        # Step 1: Get all documents with their embeddings via chunks
        # We'll cluster at the document level using average chunk embeddings
        print(f"[ML] [{timestamp}] Fetching document embeddings...")

        # Get documents with text for label generation
        # Use a fresh query to avoid stale session issues
        docs = self.db.exec(select(Document).limit(5000)).all()
        if len(docs) < min_cluster_size:
            print(f"[ML] [{timestamp}] Not enough documents for clustering ({len(docs)} < {min_cluster_size})")
            return 0

        # Extract document data immediately to avoid session staleness during long clustering
        doc_data = []
        for doc in docs:
            try:
                if doc.raw_text and len(doc.raw_text) > 50:
                    doc_data.append({
                        'id': doc.id,
                        'raw_text': doc.raw_text
                    })
            except Exception:
                # Document may have been deleted - skip it
                continue

        if len(doc_data) < min_cluster_size:
            print(f"[ML] [{timestamp}] Not enough valid documents ({len(doc_data)} < {min_cluster_size})")
            return 0

        # Get embeddings for documents (use first chunk of each)
        doc_embeddings = []
        doc_ids = []
        doc_texts = []

        for doc_info in doc_data:
            # Get the embedding from embedder (it may be cached or need to generate)
            raw_text = doc_info['raw_text']
            if raw_text and len(raw_text) > 50:
                try:
                    # Use first 1000 chars for embedding (representative sample)
                    text_sample = raw_text[:1000]
                    embedding = self.embedder.embed(text_sample)
                    if embedding is not None and len(embedding) > 0:
                        doc_embeddings.append(embedding)
                        doc_ids.append(doc_info['id'])
                        doc_texts.append(raw_text[:500])  # For label generation
                except Exception:
                    continue

        if len(doc_embeddings) < min_cluster_size:
            print(f"[ML] [{timestamp}] Not enough valid embeddings ({len(doc_embeddings)} < {min_cluster_size})")
            return 0

        print(f"[ML] [{timestamp}] Got {len(doc_embeddings)} embeddings, reducing dimensions...")

        # Step 2: Reduce dimensions (1024 -> 10-15 dimensions)
        embeddings_array = np.array(doc_embeddings)

        # Try UMAP first, fall back to PCA if numba fails on Windows
        try:
            n_neighbors = min(15, len(doc_embeddings) - 1)
            reducer = umap.UMAP(
                n_components=min(10, len(doc_embeddings) - 1),
                n_neighbors=n_neighbors,
                min_dist=0.1,
                metric='cosine',
                random_state=42
            )
            reduced_embeddings = reducer.fit_transform(embeddings_array)
            print(f"[ML] [{timestamp}] Reduced dimensions with UMAP")
        except Exception as umap_err:
            print(f"[ML] [{timestamp}] UMAP failed ({umap_err}), using PCA fallback...")
            from sklearn.decomposition import PCA
            n_components = min(10, len(doc_embeddings) - 1, embeddings_array.shape[1])
            pca = PCA(n_components=n_components, random_state=42)
            reduced_embeddings = pca.fit_transform(embeddings_array)
            print(f"[ML] [{timestamp}] Reduced dimensions with PCA")

        print(f"[ML] [{timestamp}] Running HDBSCAN clustering...")

        # Step 3: Cluster with HDBSCAN
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        cluster_labels = clusterer.fit_predict(reduced_embeddings)

        # Count clusters (excluding noise labeled as -1)
        unique_clusters = set(cluster_labels) - {-1}
        num_clusters = len(unique_clusters)

        print(f"[ML] [{timestamp}] Found {num_clusters} clusters, updating database...")

        # Step 4: Clear old clusters and create new ones
        self.db.exec(select(Cluster)).all()  # Force load
        from sqlalchemy import delete
        self.db.execute(delete(Cluster))

        # Step 5: Create cluster records with auto-generated labels
        cluster_info = {}
        for label in unique_clusters:
            # Get documents in this cluster
            cluster_doc_indices = [i for i, l in enumerate(cluster_labels) if l == label]
            cluster_texts = [doc_texts[i] for i in cluster_doc_indices]

            # Generate label from common words
            cluster_label = self._generate_cluster_label(cluster_texts)

            cluster = Cluster(
                id=int(label) + 1,  # 1-indexed
                label=cluster_label,
                description=f"Auto-generated cluster with {len(cluster_doc_indices)} documents",
                document_count=len(cluster_doc_indices)
            )
            self.db.add(cluster)
            cluster_info[label] = cluster.id

        # Step 6: Update documents with cluster assignments
        for i, (doc_id, label) in enumerate(zip(doc_ids, cluster_labels)):
            if label != -1:  # Not noise
                # Update document's cluster_id
                doc = self.db.get(Document, doc_id)
                if doc:
                    doc.cluster_id = cluster_info[label]

        try:
            self.db.commit()
            print(f"[ML] [{timestamp}] Saved {num_clusters} clusters to database")
        except Exception as e:
            print(f"[ML] [{timestamp}] Failed to save clusters: {e}")
            self.db.rollback()

        return num_clusters

    def _generate_cluster_label(self, texts: List[str], top_k: int = 3) -> str:
        """Generate a descriptive label for a cluster from its documents"""
        # Combine all texts
        combined = " ".join(texts)
        words = combined.lower().split()

        # Extended stop words
        stop_words = {
            "the", "is", "at", "which", "on", "a", "an", "and", "or", "but",
            "in", "with", "to", "for", "of", "this", "that", "it", "be", "as",
            "are", "was", "were", "been", "being", "have", "has", "had", "do",
            "does", "did", "will", "would", "could", "should", "may", "might",
            "must", "shall", "can", "need", "from", "by", "about", "into",
            "through", "during", "before", "after", "above", "below", "between",
            "under", "again", "further", "then", "once", "here", "there", "when",
            "where", "why", "how", "all", "each", "few", "more", "most", "other",
            "some", "such", "no", "nor", "not", "only", "own", "same", "so",
            "than", "too", "very", "just", "also", "now", "re", "ve", "ll",
            "hi", "hello", "thanks", "thank", "please", "regards", "best",
            "sent", "from", "subject", "date", "email", "mailto", "http", "https",
            "www", "com", "org", "net", "au", "gmail", "outlook"
        }

        # Filter and count words
        words = [w.strip(".,!?;:()[]{}\"'<>") for w in words
                 if w not in stop_words and len(w) > 3 and w.isalpha()]

        counter = Counter(words)
        top_words = [word.capitalize() for word, _ in counter.most_common(top_k)]

        if top_words:
            return " / ".join(top_words)
        return "Miscellaneous"

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
