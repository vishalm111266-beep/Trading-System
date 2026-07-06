"""Mem0 memory provider implementation."""

from typing import List, Dict, Any, Optional
import logging
from memory_memory.base import BaseMemoryProvider, MemoryEntry

logger = logging.getLogger(__name__)
class Mem0MemoryProvider(BaseMemoryProvider):
    """Memory provider using Mem0 as backend."""

    def __init__(self):
        self.client = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            from mem0 import Memory
            self.client = Memory(config)
            return True
        except ImportError:
            logger.error("Mem0 not installed. Install with: pip install mem0")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Mem0: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        try:
            if not self.client:
                return None

            results = self.client.search(
                query="",
                user_id=key,
                limit=1
            )

            if results["results"]:
                return results["results"][0]["memory"]
            return None
        except Exception as e:
            logger.error(f"Failed to get key {key} from Mem0: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            if not self.client:
                return False

            if metadata is None:
                metadata = {}

            if ttl is not None:
                metadata["ttl"] = ttl

            self.client.add(
                messages=[{"role": "user", "content": value}],
                user_id=key,
                metadata=metadata
            )
            return True
        except Exception as e:
            logger.error(f"Failed to set key {key} in Mem0: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            if not self.client:
                return False

            results = self.client.search(
                query="",
                user_id=key,
                limit=100
            )

            if results["results"]:
                for result in results["results"]:
                    self.client.delete_memory(result["id"])

            return True
        except Exception as e:
            logger.error(f"Failed to delete key {key} from Mem0: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            value = await self.get(key)
            return value is not None
        except Exception:
            return False

    async def clear(self) -> bool:
        try:
            if not self.client:
                return False

            self.client.delete_all()
            return True
        except Exception as e:
            logger.error(f"Failed to clear Mem0: {e}")
            return False

    async def keys(self) -> List[str]:
        try:
            if not self.client:
                return []

            results = self.client.list()
            return [result["id"] for result in results]
        except Exception as e:
            logger.error(f"Failed to get keys from Mem0: {e}")
            return []

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            if not self.client:
                return None

            results = self.client.search(
                query="",
                user_id=key,
                limit=1
            )

            if results["results"]:
                return results["results"][0]["metadata"]
            return None
        except Exception as e:
            logger.error(f"Failed to get metadata for key {key} from Mem0: {e}")
            return None

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            if not self.client:
                return []

            results = self.client.search(
                query=query,
                limit=limit
            )

            return [
                {
                    "id": result["id"],
                    "memory": result["memory"],
                    "metadata": result["metadata"],
                    "similarity": result.get("similarity", 0)
                }
                for result in results["results"]
            ]
        except Exception as e:
            logger.error(f"Failed to search in Mem0: {e}")
            return []

    async def health_check(self) -> bool:
        try:
            if self.client is None:
                return await self.initialize({})

            test_key = f"health_check_{self.__class__.__name__}"
            await self.set(test_key, {"test": True})
            result = await self.get(test_key)
            await self.delete(test_key)

            return result is not None
        except Exception as e:
            logger.error(f"Mem0 health check failed: {e}")
            return False