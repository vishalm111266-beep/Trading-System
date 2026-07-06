"""
Provider implementations for memory storage.

This module contains concrete implementations of memory providers that adhere to
the BaseMemoryProvider interface.
"""
from memory_memory.providers.chromadb_provider import ChromaDBMemoryProvider
from memory_memory.providers.cognee_provider import CogneeMemoryProvider
from memory_memory.providers.duckdb_provider import DuckDBMemoryProvider
from memory_memory.providers.mem0_provider import Mem0MemoryProvider
from memory_memory.registry import MemoryProviderRegistry

# Register built-in providers
MemoryProviderRegistry.register('chromadb', ChromaDBMemoryProvider)
MemoryProviderRegistry.register('duckdb', DuckDBMemoryProvider)
MemoryProviderRegistry.register('mem0', Mem0MemoryProvider)
MemoryProviderRegistry.register('cognee', CogneeMemoryProvider)
