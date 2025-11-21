"""Vector database integration with Qdrant"""

from typing import Optional, Union, List
from uuid import UUID
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import numpy as np


class VectorDB:
    """Manages vector storage and search with Qdrant"""

    def __init__(self, path: Optional[Union[str, Path]] = None, collection_name: str = "documents"):
        if path is None:
            path = Path.home() / ".mydata" / "qdrant"
        else:
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        self.client = QdrantClient(path=str(path))
        self.collection_name = collection_name
        self._initialized = False

    def initialize(self, dimension: int = 4096) -> None:
        """Initialize collection if it doesn't exist"""
        if self._initialized:
            return

        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
            )
            print(f"✓ Created Qdrant collection: {self.collection_name}")
        else:
            print(f"✓ Using existing Qdrant collection: {self.collection_name}")

        self._initialized = True

    def upsert(
        self,
        doc_id: Union[str, UUID],
        vector: Union[List[float], np.ndarray],
        payload: Optional[dict] = None,
    ) -> None:
        """Insert or update a vector"""
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()

        point = PointStruct(
            id=str(doc_id),
            vector=vector,
            payload=payload or {},
        )

        self.client.upsert(collection_name=self.collection_name, points=[point])

    def upsert_batch(
        self,
        doc_ids: List[Union[str, UUID]],
        vectors: Union[List[List[float]], np.ndarray],
        payloads: Optional[List[dict]] = None,
    ) -> None:
        """Insert or update multiple vectors"""
        if isinstance(vectors, np.ndarray):
            vectors = vectors.tolist()

        if payloads is None:
            payloads = [{} for _ in doc_ids]

        points = [
            PointStruct(id=str(doc_id), vector=vector, payload=payload)
            for doc_id, vector, payload in zip(doc_ids, vectors, payloads)
        ]

        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        query_vector: Union[List[float], np.ndarray],
        limit: int = 10,
        score_threshold: Optional[float] = None,
        filter_dict: Optional[dict] = None,
    ) -> List[dict]:
        """Search for similar vectors"""
        if isinstance(query_vector, np.ndarray):
            query_vector = query_vector.tolist()

        # Build filter if provided
        query_filter = None
        if filter_dict:
            # Simple tag filter example
            if "tag" in filter_dict:
                query_filter = Filter(
                    must=[FieldCondition(key="tags", match=MatchValue(value=filter_dict["tag"]))]
                )

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=query_filter,
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]

    def get(self, doc_id: Union[str, UUID]) -> Optional[dict]:
        """Get a specific vector by ID"""
        try:
            point = self.client.retrieve(
                collection_name=self.collection_name, ids=[str(doc_id)]
            )
            if point:
                return {
                    "id": point[0].id,
                    "vector": point[0].vector,
                    "payload": point[0].payload,
                }
        except Exception:
            pass
        return None

    def delete(self, doc_id: Union[str, UUID]) -> None:
        """Delete a vector"""
        self.client.delete(collection_name=self.collection_name, points_selector=[str(doc_id)])

    def count(self) -> int:
        """Get total number of vectors"""
        return self.client.count(collection_name=self.collection_name).count
