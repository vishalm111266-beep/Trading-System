"""Simple file-system cache for candle data."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol


def _cache_key(symbol: Symbol, start: datetime, end: datetime) -> str:
    raw = f"{symbol}:{start.isoformat()}:{end.isoformat()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _candle_to_dict(candle: Candle) -> dict:
    return {
        "timestamp": candle.timestamp.isoformat(),
        "open": candle.open,
        "high": candle.high,
        "low": candle.low,
        "close": candle.close,
        "volume": candle.volume,
    }


def _dict_to_candle(d: dict) -> Candle:
    return Candle(
        timestamp=datetime.fromisoformat(d["timestamp"]),
        open=d["open"],
        high=d["high"],
        low=d["low"],
        close=d["close"],
        volume=d["volume"],
    )


class Cache:
    """Disk-backed JSON cache for candle series."""

    def __init__(self, directory: Path) -> None:
        self._dir = directory

    def _path(self, key: str) -> Path:
        self._dir.mkdir(parents=True, exist_ok=True)
        return self._dir / f"{key}.json"

    def get(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> list[Candle] | None:
        """Return cached candles or ``None`` on miss."""
        path = self._path(_cache_key(symbol, start, end))
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return [_dict_to_candle(d) for d in data]

    def put(
        self, symbol: Symbol, start: datetime, end: datetime, candles: list[Candle]
    ) -> None:
        """Write candles to cache."""
        path = self._path(_cache_key(symbol, start, end))
        path.write_text(json.dumps([_candle_to_dict(c) for c in candles]))

    def invalidate(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> bool:
        """Delete a cache entry. Returns ``True`` if it existed."""
        path = self._path(_cache_key(symbol, start, end))
        if path.exists():
            path.unlink()
            return True
        return False
