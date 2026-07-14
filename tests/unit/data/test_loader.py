"""Tests for trading_system.data.loader."""

from datetime import datetime
from pathlib import Path
from typing import override

import pytest
from trading_system.data.cache import Cache
from trading_system.data.datasource import DataSource
from trading_system.data.loader import Loader
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

TS_START = datetime(2025, 1, 1)
TS_END = datetime(2025, 1, 31)
SYMBOL = Symbol(raw="MSFT")


class FakeSource(DataSource):
    def __init__(self, candles: list[Candle]) -> None:
        self._candles = candles
        self.call_count = 0

    @override
    def fetch_candles(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> list[Candle]:
        self.call_count += 1
        return self._candles


def _candles() -> list[Candle]:
    return [
        Candle(timestamp=datetime(2025, 1, 2), open=200, high=210, low=195, close=205, volume=500),
    ]


class TestLoader:
    def test_load_from_source(self, tmp_path: Path) -> None:
        source = FakeSource(_candles())
        loader = Loader(source, Cache(tmp_path))
        result = loader.load(SYMBOL, TS_START, TS_END)
        assert len(result) == 1
        assert source.call_count == 1

    def test_load_from_cache(self, tmp_path: Path) -> None:
        source = FakeSource(_candles())
        loader = Loader(source, Cache(tmp_path))
        loader.load(SYMBOL, TS_START, TS_END)
        loader.load(SYMBOL, TS_START, TS_END)
        assert source.call_count == 1

    def test_force_refresh(self, tmp_path: Path) -> None:
        source = FakeSource(_candles())
        loader = Loader(source, Cache(tmp_path))
        loader.load(SYMBOL, TS_START, TS_END)
        loader.load(SYMBOL, TS_START, TS_END, force_refresh=True)
        assert source.call_count == 2

    def test_validates_data(self, tmp_path: Path) -> None:
        bad = [
            Candle(timestamp=datetime(2025, 1, 2), open=100, high=90, low=95, close=100, volume=1)
        ]
        source = FakeSource(bad)
        loader = Loader(source, Cache(tmp_path))
        with pytest.raises(Exception):
            loader.load(SYMBOL, TS_START, TS_END)
