"""Tests for trading_system.data.cache."""

import json
from datetime import datetime
from pathlib import Path

from trading_system.data.cache import Cache
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

TS_START = datetime(2025, 1, 1)
TS_END = datetime(2025, 1, 31)
SYMBOL = Symbol(raw="AAPL")


def _candles() -> list[Candle]:
    return [
        Candle(timestamp=datetime(2025, 1, 2), open=100, high=110, low=95, close=105, volume=1000),
        Candle(timestamp=datetime(2025, 1, 3), open=105, high=115, low=100, close=110, volume=1200),
    ]


class TestCache:
    def test_miss_returns_none(self, tmp_path: Path) -> None:
        cache = Cache(tmp_path)
        assert cache.get(SYMBOL, TS_START, TS_END) is None

    def test_put_and_get(self, tmp_path: Path) -> None:
        cache = Cache(tmp_path)
        candles = _candles()
        cache.put(SYMBOL, TS_START, TS_END, candles)
        result = cache.get(SYMBOL, TS_START, TS_END)
        assert result is not None
        assert len(result) == 2
        assert result[0].open == 100

    def test_invalidate(self, tmp_path: Path) -> None:
        cache = Cache(tmp_path)
        cache.put(SYMBOL, TS_START, TS_END, _candles())
        assert cache.invalidate(SYMBOL, TS_START, TS_END) is True
        assert cache.get(SYMBOL, TS_START, TS_END) is None

    def test_invalidate_missing_returns_false(self, tmp_path: Path) -> None:
        cache = Cache(tmp_path)
        assert cache.invalidate(SYMBOL, TS_START, TS_END) is False

    def test_creates_directory(self, tmp_path: Path) -> None:
        sub = tmp_path / "nested" / "cache"
        cache = Cache(sub)
        cache.put(SYMBOL, TS_START, TS_END, _candles())
        assert sub.exists()

    def test_file_is_valid_json(self, tmp_path: Path) -> None:
        cache = Cache(tmp_path)
        cache.put(SYMBOL, TS_START, TS_END, _candles())
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        data = json.loads(files[0].read_text())
        assert len(data) == 2
        assert data[0]["open"] == 100
