"""Registry for memory providers."""
import logging
from importlib.metadata import entry_points

logger = logging.getLogger(__name__)


class MemoryProviderRegistry:
    """Registry for memory providers."""

    _instance = None
    _providers: dict[str, type['BaseMemoryProvider']] = {}

    def __new__(cls) -> 'MemoryProviderRegistry':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, name: str, provider_class: type['BaseMemoryProvider']) -> None:
        """Register a new provider.

        Args:
            name: Unique name for the provider
            provider_class: Provider class to register
        """
        cls._providers[name] = provider_class
        logger.info(f"Registered memory provider: {name}")

    @classmethod
    def get_provider_classes(cls) -> dict[str, type['BaseMemoryProvider']]:
        """Get all registered provider classes.

        Returns:
            Dict[str, Type['BaseMemoryProvider']]: Dictionary of provider classes
        """
        # Load built-in providers
        cls._load_builtin_providers()

        # Load plugins via entry points
        try:
            eps = entry_points(group='memory_provider')
            for ep in eps:
                cls._providers[ep.name] = ep.load()
                logger.info(f"Loaded plugin provider: {ep.name}")
        except Exception:
            pass

        return cls._providers

    @classmethod
    def _load_builtin_providers(cls) -> None:
        """Load built-in providers."""
        # Import and register built-in providers
        try:
            from memory_memory.providers.chromadb_provider import ChromaDBMemoryProvider
            cls.register('chromadb', ChromaDBMemoryProvider)
        except ImportError:
            logger.warning("ChromaDBMemoryProvider not available")

        try:
            from memory_memory.providers.mem0_provider import Mem0MemoryProvider
            cls.register('mem0', Mem0MemoryProvider)
        except ImportError:
            logger.warning("Mem0MemoryProvider not available")

        try:
            from memory_memory.providers.cognee_provider import CogneeMemoryProvider
            cls.register('cognee', CogneeMemoryProvider)
        except ImportError:
            logger.warning("CogneeMemoryProvider not available")

        try:
            from memory_memory.providers.duckdb_provider import DuckDBMemoryProvider
            cls.register('duckdb', DuckDBMemoryProvider)
        except ImportError:
            logger.warning("DuckDBMemoryProvider not available")

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the provider cache."""
        cls._providers.clear()
        logger.info("Provider registry cache cleared")
