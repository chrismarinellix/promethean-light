"""Hybrid search combining vector similarity and keyword matching (BM25)"""

from typing import List, Dict
import numpy as np
from rank_bm25 import BM25Okapi


class HybridSearcher:
    """Combines vector search with BM25 keyword search for better results"""

    def __init__(self, vector_weight: float = 0.7, bm25_weight: float = 0.3):
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self._bm25_index = None
        self._doc_texts = []
        self._doc_ids = []

    def build_bm25_index(self, documents: List[Dict]) -> None:
        """Build BM25 index from documents"""
        self._doc_texts = [doc.get('text', '') for doc in documents]
        self._doc_ids = [doc.get('id') for doc in documents]

        # Tokenize documents
        tokenized_docs = [text.lower().split() for text in self._doc_texts]

        # Build BM25 index
        self._bm25_index = BM25Okapi(tokenized_docs)

    def search(
        self,
        query: str,
        vector_results: List[Dict],
        limit: int = 10
    ) -> List[Dict]:
        """
        Hybrid search combining vector and BM25 scores

        Args:
            query: Search query string
            vector_results: Results from vector search with scores
            limit: Number of results to return

        Returns:
            Re-ranked results with hybrid scores
        """
        if not self._bm25_index:
            # No BM25 index, return vector results as-is
            return vector_results[:limit]

        # Get BM25 scores for query
        query_tokens = query.lower().split()
        bm25_scores = self._bm25_index.get_scores(query_tokens)

        # Create BM25 score lookup by doc ID
        bm25_lookup = {}
        for doc_id, score in zip(self._doc_ids, bm25_scores):
            bm25_lookup[doc_id] = score

        # Normalize scores to [0, 1]
        def normalize_scores(scores):
            if not scores or max(scores) == 0:
                return scores
            max_score = max(scores)
            return [s / max_score for s in scores]

        # Combine scores
        hybrid_results = []
        vector_scores = [r.get('score', 0) for r in vector_results]
        normalized_vector = normalize_scores(vector_scores)

        for i, result in enumerate(vector_results):
            doc_id = result.get('id')

            # Get BM25 score for this document
            bm25_score = bm25_lookup.get(doc_id, 0)

            # Normalize BM25 score
            normalized_bm25 = bm25_score / max(bm25_scores) if max(bm25_scores) > 0 else 0

            # Compute hybrid score
            hybrid_score = (
                self.vector_weight * normalized_vector[i] +
                self.bm25_weight * normalized_bm25
            )

            # Add to result
            result_copy = result.copy()
            result_copy['hybrid_score'] = hybrid_score
            result_copy['vector_score'] = result['score']
            result_copy['bm25_score'] = bm25_score
            hybrid_results.append(result_copy)

        # Sort by hybrid score
        hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

        return hybrid_results[:limit]
