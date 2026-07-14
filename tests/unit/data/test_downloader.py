"""Tests for trading_system.data.downloader."""

from datetime import datetime
from pathlib import Path
from typing import override

import pytest
from trading_system.data.cache import Cache
from trading_system.data.downloader import Downloader
from trading_system.data.provider import Provider
from trading_system.models.candle import Candle
from trading_system.models.symbol import Symbol

TS_START = datetime(2025, 1, 1)
TS_END = datetime(2025, 1, 31)
SYMBOL = Symbol(raw="MSFT")


def _candles() -> list[Candle]:
    return [
        Candle(
            timestamp=datetime(2025, 1, 2),
            open=200, high=210, low=195, close=205, volume=500,
        ),
    ]


class FakeProvider(Provider):
    name = "fake_dl"

    def __init__(self, candles: list[Candle]) -> None:
        self._candles = candles
        self.call_count = 0

    def connect(self) -> None:
        pass

    def disconnect(self) -> None:
        pass

    def is_available(self) -> bool:
        return True

    @override
    def fetch_candles(
        self, symbol: Symbol, start: datetime, end: datetime
    ) -> list[Candle]:
        self.call_count += 1
        return self._candles


class TestDownloader:
    def test_download_from_source(self, tmp_path: Path) -> None:
        provider = FakeProvider(_candles())
        dl = Downloader(provider, Cache(tmp_path))
        result = dl.download(SYMBOL, TS_START, TS_END)
        assert len(result) == 1
        assert provider.call_count == 1

    def test_download_from_cache(self, tmp_path: Path) -> None:
        provider = FakeProvider(_candles())
        dl = Downloader(provider, Cache(tmp_path))
        dl.download(SYMBOL, TS_START, TS_END)
        dl.download(SYMBOL, TS_START, TS_END)
        assert provider.call_count == 1

    def test_force_bypasses_cache(self, tmp_path: Path) -> None:
        provider = FakeProvider(_candles())
        dl = Downloader(provider, Cache(tmp_path))
        dl.download(SYMBOL, TS_START, TS_END)
        dl.download(SYMBOL, TS_START, TS_END, force=True)
        assert provider.call_count == 2

    def test_validates_data(self, tmp_path: Path) -> None:
        bad = [
            Candle(
                timestamp=datetime(2025, 1, 2),
                open=100, high=90, low=95, close=100, volume=1,
            )
        ]
        provider = FakeProvider(bad)
        dl = Downloader(provider, Cache(tmp_path))
        with pytest.raises(Exception):
            dl.download(SYMBOL, TS_START, TS_END)

    def test_provider_property(self, tmp_path: Path) -> None:
        provider = FakeProvider(_candles())
        dl = Downloader(provider, Cache(tmp_path))
        assert dl.provider is provider
