"""DuckDB memory provider implementation."""

from typing import List, Dict, Any, Optional
import json
import time
import logging
from memory_memory.base import BaseMemoryProvider, MemoryEntry

logger = logging.getLogger(__name__)
class DuckDBMemoryProvider(BaseMemoryProvider):
    """Memory provider using DuckDB for key-value storage."""

    def __init__(self):
        self.conn = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        try:
            import duckdb

            db_path = config.get("path", ":memory:")
            self.conn = duckdb.connect(db_path)

            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_memory (
                    key VARCHAR PRIMARY KEY,
                    value JSON,
                    ttl INTEGER,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_key ON agent_memory(key)")
            self.conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON agent_memory(created_at)")

            return True
        except Exception as e:
            logger.error(f"Failed to initialize DuckDB: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        try:
            result = self.conn.execute(
                "SELECT value FROM agent_memory WHERE key = ? AND (ttl IS NULL OR created_at + (ttl * INTERVAL '1 second') > CURRENT_TIMESTAMP)",
                (key,)
            ).fetchone()

            if result:
                value_json = result[0]
                return json.loads(value_json)
            return None
        except Exception as e:
            logger.error(f"Failed to get key {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> bool:
        try:
            value_json = json.dumps(value) if not isinstance(value, str) else value
            metadata_json = json.dumps(metadata) if metadata else None
            created_at = time.time()

            self.conn.execute(
                """
                INSERT OR REPLACE INTO agent_memory
                (key, value, ttl, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (key, value_json, ttl, metadata_json, created_at, created_at)
            )

            await self._cleanup_expired()

            return True
        except Exception as e:
            logger.error(f"Failed to set key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        try:
            self.conn.execute(
                "DELETE FROM agent_memory WHERE key = ?",
                (key,)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to delete key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        try:
            result = self.conn.execute(
                "SELECT 1 FROM agent_memory WHERE key = ? AND (ttl IS NULL OR created_at + (ttl * INTERVAL '1 second') > CURRENT_TIMESTAMP)",
                (key,)
            ).fetchone()

            return result is not None
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {e}")
            return False

    async def clear(self) -> bool:
        try:
            self.conn.execute("DELETE FROM agent_memory")
            return True
        except Exception as e:
            logger.error(f"Failed to clear table: {e}")
            return False

    async def keys(self) -> List[str]:
        try:
            results = self.conn.execute(
                "SELECT key FROM agent_memory WHERE ttl IS NULL OR created_at + (ttl * INTERVAL '1 second') > CURRENT_TIMESTAMP"
            ).fetchall()

            return [result[0] for result in results]
        except Exception as e:
            logger.error(f"Failed to get keys: {e}")
            return []

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.conn.execute(
                "SELECT metadata FROM agent_memory WHERE key = ? AND (ttl IS NULL OR created_at + (ttl * INTERVAL '1 second') > CURRENT_TIMESTAMP)",
                (key,)
            ).fetchone()

            if result:
                metadata_json = result[0]
                return json.loads(metadata_json)
            return None
        except Exception as e:
            logger.error(f"Failed to get metadata for key {key}: {e}")
            return None

    async def _cleanup_expired(self) -> None:
        """Remove expired entries."""
        try:
            self.conn.execute(
                "DELETE FROM agent_memory WHERE ttl IS NOT NULL AND created_at + (ttl * INTERVAL '1 second') <= CURRENT_TIMESTAMP"
            )
        except Exception as e:
            logger.error(f"Failed to cleanup expired entries: {e}")