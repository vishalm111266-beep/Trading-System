"""ChromaDB memory provider implementation."""

from typing import List, Dict, Any, Optional
import logging
from memory_memory.base import BaseMemoryProvider, VectorMemoryProvider, MemoryEntry

logger = logging.getLogger(__name__)
class ChromaDBMemoryProvider(VectorMemoryProvider):
    """Memory provider using ChromaDB for vector storage."""

    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "agent_memory"

    async def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            import chromadb
            from chromadb.config import Settings

            self.client = chromadb.PersistentClient(
                path=config.get("path", "./chromadb_data"),
                settings=Settings(anonymized_telemetry=False)
            )

            self.collection_name = config.get("collection_name", "agent_memory")

            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass

            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Agent memory storage"}
            )

            return True
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        try:
            results = self.collection.get(ids=[key])
            if results["ids"]:
                return results["metadatas"][0]
            return None
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            if metadata is None:
                metadata = {}

            vector = self._text_to_vector(str(value))

            if ttl:
                metadata["ttl"] = ttl

            self.collection.add(
                ids=[key],
                embeddings=[vector],
                metadatas=[metadata]
            )

            return True
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            self.collection.delete(ids=[key])
            return True
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            result = self.collection.get(ids=[key])
            return len(result["ids"]) > 0
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False

    async def clear(self) -> bool:
        try:
            try:
                self.client.delete_collection(self.collection_name)
            except Exception:
                pass

            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Agent memory storage"}
            )

            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False

    async def keys(self) -> List[str]:
        try:
            results = self.collection.get(limit=10000)
            return results["ids"]
        except Exception as e:
            logger.error(f"Failed to get keys: {e}")
            return []

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.collection.get(ids=[key])
            if result["ids"]:
                return result["metadatas"][0]
            return None
        except Exception as e:
            logger.error(f"Failed to get metadata for key {key}: {e}")
            return None

    async def add_vector(self, key: str, vector: List[float],
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            if metadata is None:
                metadata = {}

            self.collection.add(
                ids=[key],
                embeddings=[vector],
                metadatas=[metadata]
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add vector for key {key}: {e}")
            return False

    async def query_vectors(self, query_vector: List[float],
                           limit: int = 10) -> List[Dict[str, Any]]:
        try:
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=limit
            )

            return [
                {
                    "key": result_id,
                    "vector": result_vector,
                    "metadata": result_metadata,
                    "distance": distance
                }
                for result_id, result_vector, result_metadata, distance
                in zip(
                    results["ids"][0],
                    results["embeddings"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ]
        except Exception as e:
            logger.error(f"Failed to query vectors: {e}")
            return []

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            query_vector = self._text_to_vector(query)
            return await self.query_vectors(query_vector, limit)
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            return []

    def _text_to_vector(self, text: str) -> List[float]:
        """Convert text to vector using simple hashing."""
        import hashlib
        import numpy as np
        from numpy.linalg import norm

        h = hashlib.md5(text.encode())
        seed = int(h.hexdigest()[:8], 16)
        rng = np.random.RandomState(seed)
        vec = rng.randn(4)
        return (vec / norm(vec)).tolist()