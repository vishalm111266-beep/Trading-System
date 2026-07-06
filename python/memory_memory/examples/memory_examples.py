"""
Memory Provider Example: Demonstrating the provider abstraction pattern.

This example shows:
1. Using multiple memory providers
2. Switching between providers
3. Configuring provider hierarchies
4. Migration between providers
"""
import asyncio
import logging
import sys
from pathlib import Path
from typing import Any

# Add the project to the path
sys_path = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, sys_path)

from memory_memory.memory.manager import MemoryManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def basic_usage_example():
    """Example 1: Basic usage of Memory Manager with multiple providers."""
    logger.info("=== Basic Usage Example ===")

    # Configure memory system with multiple providers
    config = {
        "default": "chromadb",
        "providers": {
            "duckdb": {
                "enabled": True,
                "path": "./data/memory.duckdb"
            },
            "chromadb": {
                "enabled": True,
                "path": "./data/chromadb",
                "collection_name": "agent_memory"
            }
        }
    }

    # Initialize memory manager
    memory = MemoryManager(config)

    logger.info(f"Available providers: {await memory.list_providers()}")

    # Store and retrieve data using default provider (ChromaDB)
    await memory.set("strategy_001", {
        "name": "Momentum Breakout",
        "description": "Buy when price breaks above 20-day high",
        "risk_score": 0.7
    })

    data = await memory.get("strategy_001")
    logger.info(f"Retrieved data: {data}")

    # Store the same data in DuckDB for backup
    await memory.set("strategy_001", {
        "name": "Momentum Breakout",
        "description": "Buy when price breaks above 20-day high",
        "risk_score": 0.7
    }, provider="duckdb")

    # Retrieve from DuckDB
    duckdb_data = await memory.get("strategy_001", provider="duckdb")
    logger.info(f"Retrieved from DuckDB: {duckdb_data}")

    # List all keys in each provider
    chromadb_keys = await memory.keys("chromadb")
    duckdb_keys = await memory.keys("duckdb")

    logger.info(f"ChromaDB keys: {chromadb_keys}")
    logger.info(f"DuckDB keys: {duckdb_keys}")

    logger.info("Basic usage example completed.\n")
async def provider_switching_example():
    """Example 2: Switching between providers dynamically."""
    logger.info("=== Provider Switching Example ===")

    config = {
        "default": "duckdb",
        "providers": {
            "duckdb": {
                "enabled": True,
                "path": ":memory:"
            },
            "chromadb": {
                "enabled": True,
                "path": "./data/chromadb"
            }
        }
    }

    memory = MemoryManager(config)

    # Start with DuckDB
    logger.info("Using DuckDB as primary provider")
    await memory.set("test_key", "test_value", provider="duckdb")
    value = await memory.get("test_key", provider="duckdb")
    logger.info(f"Value from DuckDB: {value}")

    # Switch to ChromaDB for vector operations
    logger.info("Switching to ChromaDB for vector storage")
    await memory.switch_provider("chromadb", {
        "enabled": True,
        "path": "./data/chromadb",
        "collection_name": "vectors"
    })

    # Store a vector
    import numpy as np
    vector = np.random.rand(4).tolist()
    await memory.set("vector_001", vector, provider="chromadb")
    logger.info(f"Stored vector: {vector}")

    # Query similar vectors
    similar = await memory.search("trend following", provider="chromadb", limit=5)
    logger.info(f"Found {len(similar)} similar vectors")

    logger.info("Provider switching example completed.\n")
async def migration_example():
    """Example 3: Migrating data between providers."""
    logger.info("=== Migration Example ===")

    # Create source data in DuckDB
    source_config = {
        "providers": {
            "duckdb": {
                "enabled": True,
                "path": "./data/source.duckdb"
            }
        }
    }

    # Create target for ChromaDB
    target_config = {
        "providers": {
            "chromadb": {
                "enabled": True,
                "path": "./data/target.chromadb"
            }
        }
    }

    # Initialize source and target
    source_memory = MemoryManager(source_config)
    target_memory = MemoryManager(target_config)

    # Add data to source
    await source_memory.set("data_001", {"value": 123, "category": "test"})
    await source_memory.set("data_002", {"value": 456, "category": "production"})
    await source_memory.set("data_003", {"value": 789, "category": "test"})

    logger.info("Source provider initialized with data")

    # Perform migration
    logger.info("Initiating migration from DuckDB to ChromaDB...")
    success = await source_memory.migrate_data("duckdb", "chromadb")

    if success:
        logger.info("Migration successful!")

        # Verify data in target
        keys = await target_memory.keys("chromadb")
        logger.info(f"Target now has {len(keys)} keys: {keys}")
    else:
        logger.error("Migration failed")

    logger.info("Migration example completed.\n")
async def agent_integration_example():
    """Example 4: Integrating with agent systems."""
    logger.info("=== Agent Integration Example ===")


    config = {
        "default": "agent_memory",
        "providers": {
            "agent_memory": {
                "enabled": True,
                "config_file": "./config/agent_memory.yaml"
            },
            "chromadb": {
                "enabled": True,
                "path": "./data/chromadb"
            }
        }
    }

    memory = MemoryManager(config)

    class Agent:
        def __init__(self, agent_id: str):
            self.agent_id = agent_id
            self.memory = memory

        async def remember(self, key: str, value: Any, ttl: int | None = None) -> bool:
            """Remember information in agent's memory."""
            full_key = f"{self.agent_id}:{key}"
            return await self.memory.set(full_key, value, ttl=ttl)

        async def recall(self, key: str) -> Any:
            """Recall information from agent's memory."""
            full_key = f"{self.agent_id}:{key}"
            return await self.memory.get(full_key)

        async def search_memory(self, query: str, limit: int = 10) -> list:
            """Search agent's memory for information."""
            # Use ChromaDB for semantic search
            return await self.memory.search(query, provider="chromadb", limit=limit)

        async def clear_memories(self) -> bool:
            """Clear all agent's memories."""
            full_key = f"{self.agent_id}:*"
            keys = await self.memory.keys()
            filtered_keys = [k for k in keys if k.startswith(f"{self.agent_id}:")]

            failed = []
            for key in filtered_keys:
                if not await self.memory.delete(key):
                    failed.append(key)

            return len(failed) == 0

    # Create an agent
    trader_agent = Agent("trader_123")

    # Agent remembers market analysis
    await trader_agent.remember("market_analysis", {
        "last_price": 150.25,
        "volume": "high",
        "indicators": {"rsi": 65, "macd": "bullish"}
    }, ttl=3600)

    # Agent recalls the analysis
    analysis = await trader_agent.recall("market_analysis")
    logger.info(f"Agent recalled analysis: {analysis}")

    # Store vector representation for similarity search
    import numpy as np
    vector = np.random.rand(4).tolist()
    await memory.set(f"{trader_agent.agent_id}:vector", vector, provider="chromadb")
    logger.info("Stored vector representation")

    # Search for similar market conditions
    similar = await trader_agent.search_memory("high volume bullish rsi", limit=3)
    logger.info(f"Found {len(similar)} similar market conditions")

    logger.info("Agent integration example completed.\n")
async def health_check_example():
    """Example 5: Checking provider health."""
    logger.info("=== Health Check Example ===")

    config = {
        "providers": {
            "duckdb": {
                "enabled": True,
                "path": "./data/health_check.duckdb"
            },
            "chromadb": {
                "enabled": True,
                "path": "./data/health_check.chromadb"
            }
        }
    }

    memory = MemoryManager(config)

    # Check health of all providers
    health_status = await memory.health_check()
    logger.info(f"Provider health status: {health_status}")

    # Perform individual health checks
    for provider_name in health_status:
        is_healthy = health_status[provider_name]
        status = "HEALTHY" if is_healthy else "UNHEALTHY"
        logger.info(f"{provider_name}: {status}")

    logger.info("Health check example completed.\n")
async def main():
    """Run all examples."""
    logger.info("Starting memory provider examples...\n")

    try:
        await basic_usage_example()
        await provider_switching_example()
        await migration_example()
        await agent_integration_example()
        await health_check_example()

        logger.info("All examples completed successfully!")

    except Exception as e:
        logger.error(f"Example failed with error: {e}")
        raise
if __name__ == "__main__":
    asyncio.run(main())
