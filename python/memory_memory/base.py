import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from typing import Any

logger = logging.getLogger(__name__)
@dataclass
class MemoryEntry:
    key: str
    value: Any
    ttl: int | None = None
    metadata: dict[str, Any] | None = field(default_factory=dict)
    created_at: float | None = None
    updated_at: float | None = None
class BaseMemoryProvider(ABC):
    """Abstract base class for all memory providers."""

    @abstractmethod
    async def initialize(self, config: dict[str, Any]) -> bool:
        """Initialize the memory provider.

        Args:
            config: Provider-specific configuration

        Returns:
            bool: True if initialization successful
        """

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Retrieve a value from memory by key.

        Args:
            key: Memory key to retrieve

        Returns:
            Optional[Any]: Retrieved value or None if not found
        """

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None,
                 metadata: dict[str, Any] | None = None) -> bool:
        """Store a value in memory.

        Args:
            key: Memory key
            value: Value to store
            ttl: Optional time-to-live in seconds
            metadata: Optional metadata for the entry

        Returns:
            bool: True if storage successful
        """

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key from memory.

        Args:
            key: Memory key to delete

        Returns:
            bool: True if deletion successful
        """

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if a key exists in memory.

        Args:
            key: Memory key to check

        Returns:
            bool: True if key exists
        """

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all keys from memory.

        Returns:
            bool: True if clear successful
        """

    @abstractmethod
    async def keys(self) -> list[str]:
        """Get all keys in memory.

        Returns:
            List[str]: List of all memory keys
        """

    @abstractmethod
    async def get_metadata(self, key: str) -> dict[str, Any] | None:
        """Get metadata for a specific key.

        Args:
            key: Memory key

        Returns:
            Optional[Dict[str, Any]]: Metadata or None if not found
        """

    async def batch_get(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple keys in a single operation.

        Args:
            keys: List of memory keys to retrieve

        Returns:
            Dict[str, Any]: Dictionary mapping keys to values
        """
        results = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                results[key] = value
        return results

    async def batch_set(self, entries: list[MemoryEntry]) -> list[str]:
        """Set multiple entries in a single operation.

        Args:
            entries: List of MemoryEntry objects to store

        Returns:
            List[str]: List of keys that failed to store
        """
        failed_keys = []
        for entry in entries:
            success = await self.set(
                entry.key,
                entry.value,
                entry.ttl,
                entry.metadata
            )
            if not success:
                failed_keys.append(entry.key)
        return failed_keys

    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search for entries matching a query.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List[Dict[str, Any]]: List of matching entries
        """
        raise NotImplementedError("Search not supported by this provider")

    async def health_check(self) -> bool:
        """Check if the provider is healthy.

        Returns:
            bool: True if provider is healthy
        """
        try:
            await self.initialize({})
            return True
        except Exception:
            return False
class VectorMemoryProvider(BaseMemoryProvider):
    """Provider for vector-based memory systems."""

    @abstractmethod
    async def add_vector(self, key: str, vector: list[float],
                         metadata: dict[str, Any] | None = None) -> bool:
        """Add a vector to memory."""

    @abstractmethod
    async def query_vectors(self, query_vector: list[float],
                           limit: int = 10) -> list[dict[str, Any]]:
        """Query vectors similar to the query vector."""
