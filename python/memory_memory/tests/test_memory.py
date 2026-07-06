"""Tests for memory provider abstraction system."""

import pytest
import asyncio
from memory_memory.memory.base import BaseMemoryProvider, MemoryEntry
from memory_memory.memory.registry import MemoryProviderRegistry
from memory_memory.memory.manager import MemoryManager
from memory_memory.memory.providers.chromadb_provider import ChromaDBMemoryProvider
from memory_memory.memory.providers.duckdb_provider import DuckDBMemoryProvider


class TestMemoryEntry:
    """Tests for MemoryEntry dataclass."""

    def test_creation(self):
        """Test MemoryEntry creation."""
        entry = MemoryEntry(key="test_key", value={"data": "test"})
        
        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.metadata == {}
        assert entry.ttl is None
        assert entry.created_at is None
        assert entry.updated_at is None

    def test_with_metadata(self):
        """Test MemoryEntry with metadata."""
        entry = MemoryEntry(
            key="test_key",
            value={"data": "test"},
            metadata={"source": "test"},
            ttl=3600
        )
        
        assert entry.key == "test_key"
        assert entry.value == {"data": "test"}
        assert entry.metadata == {"source": "test"}
        assert entry.ttl == 3600


class TestProviderRegistry:
    """Tests for MemoryProviderRegistry."""

    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        reg1 = MemoryProviderRegistry
        reg2 = MemoryProviderRegistry
        
        assert reg1 is reg2

    def test_register_provider(self):
        """Test registering a new provider."""
        class TestProvider(BaseMemoryProvider):
            async def initialize(self, config):
                return True
            
            async def get(self, key):
                return None
            
            async def set(self, key, value, ttl=None, metadata=None):
                return True
            
            async def delete(self, key):
                return True
            
            async def exists(self, key):
                return False
            
            async def clear(self):
                return True
            
            async def keys(self):
                return []
            
            async def get_metadata(self, key):
                return None

        # Clear registry cache
        MemoryProviderRegistry.clear_cache()
        
        # Register provider
        MemoryProviderRegistry.register('test_provider', TestProvider)
        
        # Get providers
        providers = MemoryProviderRegistry.get_provider_classes()
        
        assert 'test_provider' in providers
        assert providers['test_provider'] is TestProvider

    def test_default_providers(self):
        """Test that default providers are available."""
        # Clear registry cache
        MemoryProviderRegistry.clear_cache()
        
        # Get providers
        providers = MemoryProviderRegistry.get_provider_classes()
        
        # Check that built-in providers are registered
        assert 'chromadb' in providers
        assert 'duckdb' in providers
        
        assert providers['chromadb'] is ChromaDBMemoryProvider
        assert providers['duckdb'] is DuckDBMemoryProvider

    @pytest.mark.asyncio
    async def test_chromadb_provider_registration(self):
        """Test ChromaDB provider registration."""
        # Clear registry cache
        MemoryProviderRegistry.clear_cache()
        
        # Check ChromaDB is registered
        providers = MemoryProviderRegistry.get_provider_classes()
        assert 'chromadb' in providers
        
        # Create and initialize provider
        provider = providers['chromadb']()
        assert await provider.initialize({})
        
        # Test basic operations
        assert await provider.set("test_key", {"value": "test_value"})
        assert await provider.exists("test_key")
        result = await provider.get("test_key")
        assert result["value"] == "test_value"
        assert await provider.delete("test_key")
        
        # Cleanup
        await provider.clear()

    @pytest.mark.asyncio
    async def test_duckdb_provider_registration(self):
        """Test DuckDB provider registration."""
        # Clear registry cache
        MemoryProviderRegistry.clear_cache()
        
        # Check DuckDB is registered
        providers = MemoryProviderRegistry.get_provider_classes()
        assert 'duckdb' in providers
        
        # Create and initialize provider
        provider = providers['duckdb']()
        assert await provider.initialize({})
        
        # Test basic operations
        assert await provider.set("test_key", {"value": "test_value"})
        assert await provider.exists("test_key")
        result = await provider.get("test_key")
        assert result["value"] == "test_value"
        assert await provider.delete("test_key")
        
        # Cleanup
        await provider.clear()


class TestMemoryManager:
    """Tests for MemoryManager."""

    def test_initialization(self):
        """Test MemoryManager initialization."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        assert memory.default_provider_name == "duckdb"
        assert "duckdb" in memory.providers
        
        # Test getting provider
        provider = memory.get_provider()
        assert provider is memory.providers["duckdb"]

    def test_get_provider_error(self):
        """Test error when getting uninitialized provider."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Try to get non-existent provider
        with pytest.raises(KeyError):
            memory.get_provider("non_existent")

    @pytest.mark.asyncio
    async def test_get_set_operations(self):
        """Test basic get/set operations."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Test set and get
        assert await memory.set("key1", {"value": "test_value"})
        result = await memory.get("key1")
        assert result["value"] == "test_value"
        
        # Test exists
        assert await memory.exists("key1")
        
        # Test delete
        assert await memory.delete("key1")
        assert not await memory.exists("key1")
        
        # Test clear
        await memory.set("key2", "value2")
        assert await memory.clear()
        assert await memory.keys() == []

    @pytest.mark.asyncio
    async def test_provider_specific_operations(self):
        """Test operations with specific providers."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"},
                "chromadb": {"enabled": True, "path": "./data/test.chromadb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Test DuckDB operations
        assert await memory.set("duckdb_key", "duckdb_value", provider="duckdb")
        result = await memory.get("duckdb_key", provider="duckdb")
        assert result == "duckdb_value"
        
        # Test ChromaDB operations
        assert await memory.set("chromadb_key", {"vector": [0.1, 0.2]}, provider="chromadb")
        result = await memory.get("chromadb_key", provider="chromadb")
        assert result["vector"] == [0.1, 0.2]

    @pytest.mark.asyncio
    async def test_keys_operations(self):
        """Test keys() operations."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Initially empty
        assert await memory.keys() == []
        
        # Add some keys
        await memory.set("key1", "value1")
        await memory.set("key2", "value2")
        
        # Check keys
        keys = await memory.keys()
        assert "key1" in keys
        assert "key2" in keys
        
        # Cleanup
        await memory.clear()

    @pytest.mark.asyncio
    async def test_metadata_operations(self):
        """Test metadata operations."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Set with metadata
        assert await memory.set("key1", {"value": "test"}, metadata={"source": "test"})
        
        # Get metadata
        metadata = await memory.get_metadata("key1")
        assert metadata == {"source": "test"}
        
        # Cleanup
        await memory.clear()

    @pytest.mark.asyncio
    async def test_batch_operations(self):
        """Test batch get/set operations."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Test batch set
        entries = [
            MemoryEntry(key="batch_key1", value="value1"),
            MemoryEntry(key="batch_key2", value="value2"),
            MemoryEntry(key="batch_key3", value="value3")
        ]
        
        failed_keys = await memory.batch_set(entries)
        assert len(failed_keys) == 0
        
        # Test batch get
        keys = ["batch_key1", "batch_key2", "batch_key3", "non_existent_key"]
        result = await memory.batch_get(keys)
        
        assert len(result) == 3
        assert "batch_key1" in result
        assert "batch_key2" in result
        assert "batch_key3" in result
        assert "non_existent_key" not in result
        
        # Cleanup
        await memory.clear()

    @pytest.mark.asyncio
    async def test_search_operations(self):
        """Test search operations."""
        config = {
            "default": "chromadb",
            "providers": {
                "chromadb": {"enabled": True, "path": "./data/test_search.chromadb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Set test data
        await memory.set("doc1", {"content": "Machine learning with Python"})
        await memory.set("doc2", {"content": "Deep learning for trading strategies"})
        await memory.set("doc3", {"content": "AI in financial markets"})
        
        # Search for queries
        results1 = await memory.search("machine learning", limit=5)
        assert len(results1) > 0
        
        results2 = await memory.search("deep learning", limit=5)
        assert len(results2) > 0
        
        # Cleanup
        await memory.clear("chromadb")

    @pytest.mark.asyncio
    async def test_provider_switching(self):
        """Test switching between providers."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": "./data/switch_source.duckdb"},
                "chromadb": {"enabled": True, "path": "./data/switch_target.chromadb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Switch to ChromaDB
        assert await memory.switch_provider("chromadb", {
            "enabled": True,
            "path": "./data/switch_target.chromadb",
            "collection_name": "switch_test"
        })
        
        # Test operations on ChromaDB
        assert await memory.set("switch_key", "switch_value")
        result = await memory.get("switch_key")
        assert result == "switch_value"

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check for all providers."""
        config = {
            "providers": {
                "duckdb": {"enabled": True, "path": "./data/health.duckdb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Check health
        health_status = await memory.health_check()
        
        assert "duckdb" in health_status
        assert health_status["duckdb"] is True

    @pytest.mark.asyncio
    async def test_list_providers(self):
        """Test listing available providers."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": ":memory:"}
            }
        }
        
        memory = MemoryManager(config)
        
        # List providers
        providers = await memory.list_providers()
        
        assert "duckdb" in providers
        assert len(providers) == 1


class TestMemoryProviderAbstraction:
    """Integration tests for memory provider abstraction."""

    @pytest.mark.asyncio
    async def test_multiple_providers_integration(self):
        """Test integration with multiple providers."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": "./data/integration.duckdb"},
                "chromadb": {"enabled": True, "path": "./data/integration.chromadb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Test operations with both providers
        await memory.set("shared_key", "shared_value", provider="duckdb")
        assert await memory.get("shared_key", provider="duckdb") == "shared_value"
        
        await memory.set("shared_vector_key", [0.1, 0.2], provider="chromadb")
        result = await memory.get("shared_vector_key", provider="chromadb")
        assert result["vector"] == [0.1, 0.2]
        
        # Test switching providers
        await memory.switch_provider("duckdb", {"enabled": True, "path": "./data/integration.duckdb"})
        
        # Test operations with DuckDB after switch
        result = await memory.get("shared_key")
        assert result == "shared_value"

    @pytest.mark.asyncio
    async def test_memory_reliability(self):
        """Test memory operations under various conditions."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": "./data/reliability.duckdb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Test setting various data types
        await memory.set("string_key", "string_value")
        await memory.set("int_key", 123)
        await memory.set("float_key", 45.67)
        await memory.set("list_key", [1, 2, 3])
        await memory.set("dict_key", {"nested": {"data": "value"}})
        
        # Verify all types can be retrieved
        assert await memory.get("string_key") == "string_value"
        assert await memory.get("int_key") == 123
        assert await memory.get("float_key") == 45.67
        assert await memory.get("list_key") == [1, 2, 3]
        assert await memory.get("dict_key") == {"nested": {"data": "value"}}
        
        # Cleanup
        await memory.clear()

    @pytest.mark.asyncio
    async def test_ttl_functionality(self):
        """Test TTL functionality."""
        config = {
            "default": "duckdb",
            "providers": {
                "duckdb": {"enabled": True, "path": "./data/ttl.duckdb"}
            }
        }
        
        memory = MemoryManager(config)
        
        # Set with TTL (in seconds)
        await memory.set("ttl_key", "ttl_value", provider="duckdb", ttl=1)
        
        # Should exist immediately
        assert await memory.exists("ttl_key")
        assert await memory.get("ttl_key") == "ttl_value"
        
        # Cleanup
        await memory.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])