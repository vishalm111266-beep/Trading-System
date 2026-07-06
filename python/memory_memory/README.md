"""
Memory Provider Abstraction Module

This module provides a clean, extensible provider abstraction for memory systems
that supports current (AgentMemory) and future (Mem0, Cognee, etc.) providers while
maintaining backward compatibility.

## Architecture Overview

The memory system is designed with the following principles:
- **Interface Segregation**: Break down memory operations into focused interfaces
- **Plugin Architecture**: Allow new providers to be added without modifying core code
- **Adapter Pattern**: Wrap existing memory systems to conform to the abstraction
- **Configuration-Driven**: Provider selection via configuration
- **Testable**: Each provider has a unified interface for testing

## Core Interfaces

The abstraction is built around these core interfaces:

### 1. BaseMemoryProvider - Core Operations
The `BaseMemoryProvider` interface defines essential memory operations.

### 2. VectorMemoryProvider - Specialized for Vector Storage
Extends `BaseMemoryProvider` for vector-based systems like ChromaDB.

### 3. ConfigManager - Configuration Management
Handles provider configuration and settings.

## Provider Architecture

### 1. Built-in Providers
- **AgentMemory**: Wrapper for the existing AgentMemory system
- **ChromaDB**: Adapter for ChromaDB vector storage
- **DuckDB**: Adapter for DuckDB key-value storage

### 2. Plugin Architecture
- **Entry Points**: Use setuptools entry points for plugin discovery
- **Registration**: Register providers via `MemoryProviderRegistry`
- **Dynamic Loading**: Load providers at runtime

### 3. Configuration
- **INI Files**: Standard INI configuration format
- **Environment Variables**: Support for environment variable configuration
- **Hierarchical**: Multiple configuration levels (global, project, user-specific)

## Usage Examples

### Basic Usage
```python
from memory.memory import MemoryManager

async def main():
    config = {
        "default": "agent_memory",
        "providers": {
            "agent_memory": {"enabled": True},
            "chromadb": {"enabled": True, "path": "./data/chromadb"},
            "duckdb": {"enabled": True, "path": "./data/memory.duckdb"}
        }
    }

    memory = MemoryManager(config)
    
    # Store and retrieve data
    await memory.set("user_123", {"name": "Alice"})
    data = await memory.get("user_123")
    
    # Search for data
    results = await memory.search("Alice")
    
    # List all keys
    keys = await memory.keys()
```

### Provider Switching
```python
async def provider_switching_example():
    config = {
        "default": "duckdb",
        "providers": {
            "duckdb": {"enabled": True, "path": "./data/memory.duckdb"},
            "chromadb": {"enabled": True, "path": "./data/chromadb"}
        }
    }

    memory = MemoryManager(config)
    
    # Store in DuckDB
    await memory.set("vector_001", [0.1, 0.2, 0.3], provider="duckdb")
    
    # Switch to ChromaDB for vector operations
    await memory.switch_provider("chromadb", {
        "enabled": True,
        "path": "./data/chromadb",
        "collection_name": "vectors"
    })
    
    # Store a vector
    await memory.set("vector_002", [0.4, 0.5, 0.6], provider="chromadb")
```

### Integration with Agents
```python
class Agent:
    def __init__(self, agent_id: str, memory_manager: MemoryManager):
        self.agent_id = agent_id
        self.memory = memory_manager

    async def remember(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Remember information in agent's memory."""
        full_key = f"{self.agent_id}:{key}"
        return await self.memory.set(full_key, value, ttl=ttl)

    async def recall(self, key: str) -> Any:
        """Recall information from agent's memory."""
        full_key = f"{self.agent_id}:{key}"
        return await self.memory.get(full_key)
```

## Migration Strategies

### Gradual Migration
```python
async def gradual_migration():
    config = {
        "providers": {
            "duckdb": {"enabled": True, "path": "./data/source.duckdb"},
            "chromadb": {"enabled": True, "path": "./data/target.chromadb"}
        }
    }

    memory = MemoryManager(config)
    
    # Migrate data in background
    await memory.migrate_data("duckdb", "chromadb")
    
    # Update application to use ChromaDB
    await memory.set("new_key", "new_value", provider="chromadb")
    
    # Decommission DuckDB
    await memory.set("dummy_config", {"enabled": False}, provider="duckdb")
```

### Hybrid Mode
```python
class HybridMemoryManager(MemoryManager):
    """Memory manager that supports hybrid mode."""
    
    async def hybrid_set(self, key: str, value: Any, provider: Optional[str] = None) -> bool:
        """Set value using primary, fallback to secondary."""
        primary_provider = self.get_provider(provider)
        
        success = await primary_provider.set(key, value)
        if not success:
            secondary_provider = self.get_provider("duckdb")
            success = await secondary_provider.set(key, value)
        
        return success
```

## Testing

Each provider should have comprehensive tests:

```python
# tests/test_providers/test_chromadb_provider.py
import pytest
from memory.providers.chromadb_provider import ChromaDBMemoryProvider

class TestChromaDBMemoryProvider:
    @pytest.fixture
    def provider(self):
        return ChromaDBMemoryProvider()

    @pytest.mark.asyncio
    async def test_crud_operations(self, provider):
        assert await provider.initialize({"path": ":memory:"})
        assert await provider.set("key1", {"value": 123})
        assert await provider.exists("key1")
        result = await provider.get("key1")
        assert result["value"] == 123
```

## Adding New Providers

To add a new provider (e.g., Mem0):

```python
# File: memory/providers/mem0_provider.py
from memory.base import BaseMemoryProvider

class Mem0MemoryProvider(BaseMemoryProvider):
    def __init__(self):
        self.client = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            from mem0 import Memory
            self.client = Memory(config)
            return True
        except ImportError:
            return False

    # Implement all abstract methods...
```

Register the provider:

```python
# File: setup.py or pyproject.toml
[options.entry_points]
memory_provider =
    mem0 = memory.providers.mem0_provider:Mem0MemoryProvider
```

## Security Considerations

1. **Encryption**: Encrypt sensitive data before storage
2. **Access Control**: Implement authentication and authorization
3. **Audit Logging**: Log all access to sensitive data
4. **Rate Limiting**: Prevent abuse of provider APIs
5. **Secrets Management**: Store API keys securely using environment variables

## Performance Considerations

1. **Caching**: Implement local caching for frequently accessed data
2. **Batch Operations**: Use provider-specific batch operations
3. **Connection Pooling**: Maintain connection pools for database providers
4. **Async Operations**: Ensure all I/O operations are properly async
5. **Error Handling**: Implement retry logic for transient failures

## Supported Providers

### 1. AgentMemory
- **Status**: Supported (as adapter)
- **Interface**: Key-value storage with metadata
- **Use Case**: Existing AgentMemory integration

### 2. ChromaDB
- **Status**: Supported (as adapter)
- **Interface**: Vector storage with semantic search
- **Use Case**: Trading strategy storage, semantic similarity

### 3. DuckDB
- **Status**: Supported (as adapter)
- **Interface**: Key-value storage with queries
- **Use Case**: Structured data storage, backups

### 4. Mem0 (Planned)
- **Status**: Under development
- **Interface**: Memory management system
- **Use Case**: Conversational memory, agent memory

### 5. Cognee (Planned)
- **Status**: Under development
- **Interface**: Knowledge graph storage
- **Use Case**: Knowledge graphs, structured data

## Configuration Examples

### Basic Configuration
```ini
[memory]
default = "agent_memory"
migration_mode = "gradual"
backup_enabled = true

[memory.providers.agent_memory]
enabled = true
config_file = "/path/to/agent_memory/config.yaml"

[memory.providers.chromadb]
enabled = true
path = "./data/chromadb"
collection_name = "agent_memory"

[memory.providers.duckdb]
enabled = true
path = "./data/memory.duckdb"

[memory.providers.mem0]
enabled = false
api_key = "${MEM0_API_KEY}"
endpoint = "https://api.mem0.ai"
```

### Environment Variable Configuration
```bash
export MEMORY_DEFAULT_PROVIDER="chromadb"
export CHROMADB_PATH="./data/chromadb"
export DUCKDB_PATH="./data/memory.duckdb"
```

## License
MIT License

## Copyright
© 2026 Trading Team
