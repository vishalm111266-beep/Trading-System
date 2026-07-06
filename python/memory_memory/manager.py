"""Memory managers and coordinators for provider abstraction."""
import logging
from typing import Any

from memory_memory.base import BaseMemoryProvider
from memory_memory.base import MemoryEntry
from memory_memory.registry import MemoryProviderRegistry

logger = logging.getLogger(__name__)
class MemoryManager:
    """Manager for memory operations across different providers."""

    def __init__(self, config: dict[str, Any]):
        self.providers: dict[str, BaseMemoryProvider] = {}
        self.default_provider_name = config.get("default", "duckdb")
        self.providers_config = config.get("providers", {})
        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """Initialize all registered providers."""
        provider_classes = MemoryProviderRegistry.get_provider_classes()

        for name, provider_class in provider_classes.items():
            provider = provider_class()
            config = self.providers_config.get(name, {})

            if config.get("enabled", True):
                try:
                    if hasattr(provider, 'initialize'):
                        import asyncio
                        if asyncio.run(provider.initialize(config)):
                            self.providers[name] = provider
                except Exception as e:
                    logger.error(f"Failed to initialize provider {name}: {e}")

    def get_provider(self, name: str | None = None) -> BaseMemoryProvider:
        """Get a provider by name.

        Args:
            name: Provider name (uses default if None)

        Returns:
            BaseMemoryProvider: Memory provider instance

        Raises:
            KeyError: If provider not found
        """
        if name is None:
            name = self.default_provider_name

        if name not in self.providers:
            raise KeyError(f"Provider '{name}' not found or not initialized")

        return self.providers[name]

    async def get(self, key: str, provider: str | None = None) -> Any:
        """Get a value from memory_memory.

        Args:
            key: Memory key
            provider: Provider name (uses default if None)

        Returns:
            Any: Retrieved value or None if not found
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.get(key)

    async def set(self, key: str, value: Any, provider: str | None = None,
                 ttl: int | None = None, metadata: dict[str, Any] | None = None,
                 ttl_hint: str = "seconds") -> bool:
        """Set a value in memory.

        Args:
            key: Memory key
            value: Value to store
            provider: Provider name (uses default if None)
            ttl: Optional time-to-live
            metadata: Optional metadata
            ttl_hint: Unit for TTL (seconds, minutes, hours)

        Returns:
            bool: True if storage successful
        """
        memory_provider = self.get_provider(provider)

        if ttl_hint == "hours":
            ttl = ttl * 3600 if ttl else None
        elif ttl_hint == "minutes":
            ttl = ttl * 60 if ttl else None

        return await memory_provider.set(key, value, ttl, metadata)

    async def delete(self, key: str, provider: str | None = None) -> bool:
        """Delete a key from memory_memory.

        Args:
            key: Memory key
            provider: Provider name (uses default if None)

        Returns:
            bool: True if deletion successful
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.delete(key)

    async def exists(self, key: str, provider: str | None = None) -> bool:
        """Check if a key exists in memory.

        Args:
            key: Memory key
            provider: Provider name (uses default if None)

        Returns:
            bool: True if key exists
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.exists(key)

    async def clear(self, provider: str | None = None) -> bool:
        """Clear all keys from memory_memory.

        Args:
            provider: Provider name (uses default if None)

        Returns:
            bool: True if clear successful
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.clear()

    async def keys(self, provider: str | None = None) -> list[str]:
        """Get all keys in memory.

        Args:
            provider: Provider name (uses default if None)

        Returns:
            List[str]: List of all memory keys
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.keys()

    async def get_metadata(self, key: str, provider: str | None = None) -> dict[str, Any] | None:
        """Get metadata for a specific key.

        Args:
            key: Memory key
            provider: Provider name (uses default if None)

        Returns:
            Optional[Dict[str, Any]]: Metadata or None if not found
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.get_metadata(key)

    async def batch_get(self, keys: list[str], provider: str | None = None) -> dict[str, Any]:
        """Get multiple keys in a single operation.

        Args:
            keys: List of memory keys to retrieve
            provider: Provider name (uses default if None)

        Returns:
            Dict[str, Any]: Dictionary mapping keys to values
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.batch_get(keys)

    async def batch_set(self, entries: list[MemoryEntry], provider: str | None = None) -> list[str]:
        """Set multiple entries in a single operation.

        Args:
            entries: List of MemoryEntry objects to store
            provider: Provider name (uses default if None)

        Returns:
            List[str]: List of keys that failed to store
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.batch_set(entries)

    async def search(self, query: str, provider: str | None = None,
                     limit: int = 10) -> list[dict[str, Any]]:
        """Search for entries matching a query.

        Args:
            query: Search query string
            provider: Provider name (uses default if None)
            limit: Maximum number of results to return

        Returns:
            List[Dict[str, Any]]: List of matching entries
        """
        memory_provider = self.get_provider(provider)
        return await memory_provider.search(query, limit)

    async def switch_provider(self, name: str, config: dict[str, Any]) -> bool:
        """Switch to a different provider.

        Args:
            name: Provider name
            config: New configuration for the provider

        Returns:
            bool: True if switch successful
        """
        if name not in self.providers:
            provider_classes = MemoryProviderRegistry.get_provider_classes()
            if name not in provider_classes:
                return False

            provider_class = provider_classes[name]
            provider = provider_class()

            if not await self._init_provider(provider, config):
                return False

            self.providers[name] = provider
            return True

        return await self._init_provider(self.providers[name], config)

    async def _init_provider(self, provider: BaseMemoryProvider, config: dict[str, Any]) -> bool:
        """Initialize a provider with configuration."""
        try:
            if hasattr(provider, 'initialize'):
                return await provider.initialize(config)
            return False
        except Exception as e:
            logger.error(f"Failed to initialize provider: {e}")
            return False

    async def health_check(self) -> dict[str, bool]:
        """Check health of all providers.

        Returns:
            Dict[str, bool]: Dictionary mapping provider names to health status
        """
        health_status = {}
        for name, provider in self.providers.items():
            try:
                health_status[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for provider {name}: {e}")
                health_status[name] = False
        return health_status

    async def migrate_data(self, from_name: str, to_name: str) -> bool:
        """Migrate data from one provider to another.

        Args:
            from_name: Source provider name
            to_name: Target provider name

        Returns:
            bool: True if migration successful
        """
        if from_name not in self.providers or to_name not in self.providers:
            return False

        source_provider = self.providers[from_name]
        target_provider = self.providers[to_name]

        keys = await source_provider.keys()
        failed_keys = []

        for key in keys:
            value = await source_provider.get(key)
            metadata = await source_provider.get_metadata(key)

            entry = MemoryEntry(
                key=key,
                value=value,
                metadata=metadata
            )

            result = await target_provider.batch_set([entry])
            failed_keys.extend(result)

        return len(failed_keys) == 0

    async def list_providers(self) -> list[str]:
        """List all available providers.

        Returns:
            List[str]: List of provider names
        """
        return list(self.providers.keys())
